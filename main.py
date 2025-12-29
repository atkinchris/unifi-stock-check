"""UTR stock poller (super minimal)."""

import json
import re
import sys
import time
from datetime import UTC, datetime

import requests

URL = "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr"
INTERVAL = 300  # seconds
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)

print(f"Polling UTR every {INTERVAL} seconds. Ctrl+C to stop.")
while True:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        m = NEXT_DATA_RE.search(r.text)
        if not m:
            print("❌ Error: Missing __NEXT_DATA__", file=sys.stderr)
            time.sleep(INTERVAL)
            continue
        data = json.loads(m.group(1))
        product = data["props"]["pageProps"]["collection"]["products"][0]
        variants = product.get("variants") or [{}]
        status = product.get("status", "") or variants[0].get("status", "")

        ts = datetime.now(UTC).strftime("%H:%M:%S %Z")
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
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
