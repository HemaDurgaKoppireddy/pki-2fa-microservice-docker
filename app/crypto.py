import base64
import re

import pyotp
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# =========================
# STEP 5: DECRYPT SEED
# =========================

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256
    """

    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("Invalid base64 input")

    # 2. RSA/OAEP decryption
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception:
        raise ValueError("RSA decryption failed")

    # 3. Decode to string
    try:
        seed = plaintext_bytes.decode("utf-8")
    except Exception:
        raise ValueError("Decrypted data is not UTF-8")

    # 4. Validate hex seed (64 chars)
    if len(seed) != 64 or not re.fullmatch(r"[0-9a-f]{64}", seed):
        raise ValueError("Invalid seed format")

    # 5. Return seed
    return seed


# =========================
# STEP 6: TOTP FUNCTIONS
# =========================

def _hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 string
    """
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from hex seed
    """
    base32_seed = _hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,      # 30-second period
        digest="sha1",    # REQUIRED: SHA-1
    )

    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±1 time window tolerance (±30 seconds)
    """
    if not code or not code.isdigit() or len(code) != 6:
        return False

    base32_seed = _hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest="sha1",
    )

    return totp.verify(code, valid_window=valid_window)
