from datetime import datetime, timezone
import base64
import pyotp

try:
    with open("/data/seed.txt") as f:
        seed = f.read().strip()

    seed_bytes = bytes.fromhex(seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - 2FA Code: {code}")

except Exception:
    print("Seed file not found")
