"""UTR stock poller (super minimal)."""

import json
import random
import re
import sys
import time
from datetime import UTC, datetime

import requests

URL = "https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr"
INTERVAL = 300  # seconds
ERROR_INTERVAL = 10  # seconds between retries on errors
MAX_ERRORS = 5
JITTER = 5  # +/- seconds jitter around INTERVAL
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)

print(f"Polling UTR every {INTERVAL} seconds. Ctrl+C to stop.")
error_count = 0
while True:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        m = NEXT_DATA_RE.search(r.text)
        if not m:
            error_count += 1
            print("❌ Error: Missing __NEXT_DATA__", file=sys.stderr)
            if error_count > MAX_ERRORS:
                sys.exit(1)
            time.sleep(ERROR_INTERVAL)
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

        error_count = 0
        sleep_for = max(1, INTERVAL + random.uniform(-JITTER, JITTER))  # noqa: S311
        time.sleep(sleep_for)
    except KeyboardInterrupt:
        print("Stopped by user.")
        sys.exit(130)
    except Exception as exc:
        error_count += 1
        print(f"❌ Error: {exc}", file=sys.stderr)
        if error_count > MAX_ERRORS:
            sys.exit(1)
        time.sleep(ERROR_INTERVAL)
