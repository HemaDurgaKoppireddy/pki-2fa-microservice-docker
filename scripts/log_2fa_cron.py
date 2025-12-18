#!/usr/bin/env python3
from datetime import datetime, timezone

from app.crypto import generate_totp_code

SEED_FILE = "/data/seed.txt"


def main():
    try:
        # Read seed
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # Generate TOTP
        code = generate_totp_code(hex_seed)

        # UTC timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Print output (cron redirects this to file)
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    main()
