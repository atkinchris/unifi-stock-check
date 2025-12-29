"""Lightweight stock checker for the Ubiquiti UTR page."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime

import requests

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def fetch_next_data(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (stock-check-script)"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    match = NEXT_DATA_RE.search(response.text)
    if not match:
        raise ValueError("Could not locate __NEXT_DATA__ payload in page")
    return json.loads(match.group(1))


def parse_product_status(payload: dict) -> tuple[str, str]:
    product = payload["props"]["pageProps"]["collection"]["products"][0]
    status = product.get("status", "")
    variant_status = (product.get("variants") or [{}])[0].get("status", "")
    effective = status or variant_status or "Unknown"
    return effective, variant_status or status


def check_once(url: str) -> tuple[bool, str]:
    data = fetch_next_data(url)
    status, variant_status = parse_product_status(data)
    is_available = status == "Available" or variant_status == "Available"

    if is_available:
        print("UTR is AVAILABLE", end="")
        print(" \a", end="")  # terminal bell
        print()
    elif status == "ComingSoon" or variant_status == "ComingSoon":
        print("UTR is coming soon")
    else:
        print(f"UTR status: {status or variant_status or 'Unknown'}")

    return is_available, status or variant_status or "Unknown"


def main() -> int:
    url = "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr"
    watch = "--watch" in sys.argv
    interval = int(os.getenv("UTR_POLL_SECONDS", "300"))

    if not watch:
        try:
            is_available, _ = check_once(url)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to check UTR: {exc}", file=sys.stderr)
            return 1
        return 0 if is_available else 2

    print(f"Watching UTR every {interval} seconds. Ctrl+C to stop.")
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ", end="")
            is_available, status = check_once(url)
            if is_available:
                return 0
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to check UTR: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
