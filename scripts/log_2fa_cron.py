#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timezone

# 🔑 FIX: ensure /app is in Python path
sys.path.append("/app")

from app.crypto import generate_totp_code

SEED_PATH = "/data/seed.txt"

def main():
    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
