"""UTR stock poller (super minimal)."""

import json
import re
import sys
import time
from datetime import datetime

import requests

URL = "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr"
INTERVAL = 300  # seconds
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL
)

print(f"Polling UTR every {INTERVAL} seconds. Ctrl+C to stop.")
while True:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        m = NEXT_DATA_RE.search(r.text)
        if not m:
            raise RuntimeError("Missing __NEXT_DATA__")
        data = json.loads(m.group(1))
        product = data["props"]["pageProps"]["collection"]["products"][0]
        status = product.get("status", "") or (product.get("variants") or [{}])[0].get(
            "status", ""
        )

        ts = datetime.now().strftime("%H:%M:%S")
        if status == "Available":
            print(f"[{ts}] UTR is AVAILABLE \a")
            sys.exit(0)
        elif status == "ComingSoon":
            print(f"[{ts}] UTR is coming soon")
        else:
            print(f"[{ts}] UTR status: {status or 'Unknown'}")

        time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Stopped by user.")
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error: {exc}", file=sys.stderr)
