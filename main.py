"""Simple stock checker for the Ubiquiti store.

Fetches the Next.js bootstrap data embedded in the product pages and reports
each product's availability status (e.g., Available, ComingSoon).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional

import requests

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)
AVAILABILITY_TAG_RE = re.compile(r"available:[^:]+:[^:]+:date:(\d{4}-\d{2}-\d{2})")


@dataclass
class ProductAvailability:
    title: str
    sku: str
    url: str
    status: str
    variant_status: str
    available_on: Optional[date]

    @property
    def is_available(self) -> bool:
        return self.status == "Available" or self.variant_status == "Available"

    @property
    def display_status(self) -> str:
        if self.is_available:
            return "Available"
        if self.status == "ComingSoon" or self.variant_status == "ComingSoon":
            if self.available_on:
                return f"Coming soon (available {self.available_on.isoformat()})"
            return "Coming soon"
        return self.status or self.variant_status or "Unknown"


def fetch_next_data(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (stock-check-script)"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    match = NEXT_DATA_RE.search(response.text)
    if not match:
        raise ValueError("Could not locate __NEXT_DATA__ payload in page")
    return json.loads(match.group(1))


def parse_products(url: str, payload: dict) -> List[ProductAvailability]:
    products = payload["props"]["pageProps"]["collection"]["products"]
    parsed: List[ProductAvailability] = []
    for product in products:
        tags = product.get("tags", [])
        available_on = _extract_available_date(tags)
        variants = product.get("variants", []) or [{}]
        variant_status = variants[0].get("status", "")
        parsed.append(
            ProductAvailability(
                title=product.get("title", "Unknown product"),
                sku=product.get("variants", [{}])[0].get("sku", ""),
                url=url,
                status=product.get("status", ""),
                variant_status=variant_status,
                available_on=available_on,
            )
        )
    return parsed


def _extract_available_date(tags: Iterable[dict]) -> Optional[date]:
    for tag in tags:
        name = tag.get("name", "") if isinstance(tag, dict) else str(tag)
        match = AVAILABILITY_TAG_RE.search(name)
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
    return None


def check_urls(urls: List[str]) -> List[ProductAvailability]:
    results: List[ProductAvailability] = []
    for url in urls:
        try:
            data = fetch_next_data(url)
            results.extend(parse_products(url, data))
        except Exception as exc:  # noqa: BLE001
            print(f"❌ {url}: {exc}", file=sys.stderr)
    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check stock on the Ubiquiti store")
    parser.add_argument(
        "urls",
        nargs="*",
        default=[
            "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr",
            "https://uk.store.ui.com/uk/en/category/wifi-bridging/products/udb-pro-sector",
        ],
        help="Product URLs to check",
    )
    args = parser.parse_args(argv)

    products = check_urls(args.urls)
    if not products:
        print("No products found.")
        return 1

    print("Stock status:\n")
    for product in products:
        status = product.display_status
        available_date = (
            f" (expected {product.available_on.isoformat()})"
            if product.available_on
            else ""
        )
        print(
            f"- {product.title} [{product.sku}] @ {product.url}\n  Status: {status}{available_date}\n"
        )

    in_stock = any(p.is_available for p in products)
    return 0 if in_stock else 2


if __name__ == "__main__":
    raise SystemExit(main())
