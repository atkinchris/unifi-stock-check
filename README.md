# UniFi stock checker

Tiny helper script to check Ubiquiti UK store product availability by reading
the embedded Next.js JSON from product pages.

## Usage

1. Activate the provided virtual environment:

   ```bash
   source .venv/bin/activate
   ```

2. Run the checker (defaults to the UniFi Travel Router and the Device Bridge Pro Sector sample):

   ```bash
   python main.py
   ```

3. Optionally supply your own product URLs:

   ```bash
   python main.py https://uk.store.ui.com/uk/en/category/wifi-special-devices/products/utr \
   					https://uk.store.ui.com/uk/en/category/wifi-bridging/products/udb-pro-sector
   ```

Exit code is 0 if at least one product is available, 2 otherwise.
