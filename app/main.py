import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization

from app.crypto import (
    decrypt_seed,
    generate_totp_code,
    verify_totp_code,
)

# --------------------
# App setup
# --------------------

app = FastAPI()

DATA_DIR = "/data"
SEED_FILE = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_PATH = "student_private.pem"


# --------------------
# Load private key once
# --------------------

def load_private_key():
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None,
            )
    except Exception:
        raise RuntimeError("Failed to load private key")


private_key = load_private_key()


# --------------------
# Request models
# --------------------

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str


# ====================
# Endpoint 1: POST /decrypt-seed
# ====================

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    try:
        seed = decrypt_seed(payload.encrypted_seed, private_key)

        os.makedirs(DATA_DIR, exist_ok=True)

        with open(SEED_FILE, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Decryption failed"},
        )


# ====================
# Endpoint 2: GET /generate-2fa
# ====================

@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"},
        )

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp_code(hex_seed)

        # remaining seconds in current 30s window
        valid_for = 30 - (int(time.time()) % 30)

        return {
            "code": code,
            "valid_for": valid_for,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"},
        )


# ====================
# Endpoint 3: POST /verify-2fa
# ====================

@app.post("/verify-2fa")
def verify_2fa(payload: VerifyCodeRequest):
    if not payload.code:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing code"},
        )

    if not os.path.exists(SEED_FILE):
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"},
        )

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        is_valid = verify_totp_code(hex_seed, payload.code)

        return {"valid": is_valid}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"},
        )
