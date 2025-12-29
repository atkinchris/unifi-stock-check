"""UTR stock poller (throwaway, single purpose)."""

import json
import re
import sys
import time
from datetime import datetime

import requests

URL = "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr"
INTERVAL_SECONDS = 300  # 5 minutes

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def fetch_status() -> str:
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    m = NEXT_DATA_RE.search(resp.text)
    if not m:
        raise RuntimeError("Could not find __NEXT_DATA__")
    data = json.loads(m.group(1))
    product = data["props"]["pageProps"]["collection"]["products"][0]
    status = product.get("status", "")
    variant_status = (product.get("variants") or [{}])[0].get("status", "")
    return status or variant_status or "Unknown"


def run() -> int:
    print(f"Polling UTR every {INTERVAL_SECONDS} seconds. Ctrl+C to stop.")
    try:
        while True:
            try:
                status = fetch_status()
                ts = datetime.now().strftime("%H:%M:%S")
                if status == "Available":
                    print(f"[{ts}] UTR is AVAILABLE \a")
                    return 0
                elif status == "ComingSoon":
                    print(f"[{ts}] UTR is coming soon")
                else:
                    print(f"[{ts}] UTR status: {status}")
            except Exception as exc:  # noqa: BLE001
                print(f"❌ Error: {exc}", file=sys.stderr)
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Stopped by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(run())
