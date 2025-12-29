# UniFi UTR stock poller

Checks the Ubiquiti UK store UTR page in a loop and rings the terminal bell when available.

## Run

```bash
source .venv/bin/activate
python main.py
```

Ctrl+C to stop. Exits 0 when UTR is available, 130 on Ctrl+C, 1 on repeated errors.
