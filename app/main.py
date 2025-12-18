from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

from app.crypto import load_private_key, decrypt_seed
from app.totp_utils import generate_totp, verify_totp

app = FastAPI()
PRIVATE_KEY = load_private_key()


@app.post("/decrypt-seed")
def decrypt_seed_api(payload: dict):
    try:
        encrypted_seed = payload.get("encrypted_seed")
        if not encrypted_seed:
            raise ValueError

        seed = decrypt_seed(encrypted_seed, PRIVATE_KEY)
        os.makedirs("/data", exist_ok=True)

        with open("/data/seed.txt", "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"}
        )


@app.get("/generate-2fa")
def generate_2fa():
    try:
        if not os.path.exists("/data/seed.txt"):
            raise FileNotFoundError

        seed = open("/data/seed.txt").read().strip()
        code, valid_for = generate_totp(seed)

        return {"code": code, "valid_for": valid_for}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"}
        )


@app.post("/verify-2fa")
def verify_2fa(payload: dict):
    if "code" not in payload:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"}
        )

    try:
        if not os.path.exists("/data/seed.txt"):
            raise FileNotFoundError

        seed = open("/data/seed.txt").read().strip()
        valid = verify_totp(seed, payload["code"])

        return {"valid": valid}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"}
        )
