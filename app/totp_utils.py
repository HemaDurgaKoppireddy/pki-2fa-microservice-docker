import base64
import pyotp
import time


def generate_totp(hex_seed: str):
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)

    return code, valid_for


def verify_totp(hex_seed: str, code: str):
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
    return totp.verify(code, valid_window=1)
