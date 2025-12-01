from pathlib import Path
import sys
import time

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Ensure project root is on sys.path (useful when running scripts locally)
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.crypto_utils import load_student_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, verify_totp_code


# In Docker, /data will be a volume. Locally it's just a folder at root.
DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"

app = FastAPI()


# ============
# Request models
# ============

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str | None = None


# ============
# Health check (optional but useful)
# ============

@app.get("/health")
def health():
    return {"status": "ok"}


# ============
# Endpoint 1: POST /decrypt-seed
# ============

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    """
    POST /decrypt-seed

    Request:
      { "encrypted_seed": "BASE64_STRING..." }

    Response (200):
      { "status": "ok" }

    Response (500):
      { "error": "Decryption failed" }
    """
    try:
        # Load student private key
        private_key = load_student_private_key()

        # Decrypt (decrypt_seed does base64 decode + RSA/OAEP-SHA256)
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)

        # Ensure /data exists, then save seed
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SEED_FILE.write_text(hex_seed)

        return {"status": "ok"}

    except Exception:
        # Do not leak internal error details to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Decryption failed"},
        )


# ============
# Endpoint 2: GET /generate-2fa
# ============

@app.get("/generate-2fa")
def generate_2fa():
    """
    GET /generate-2fa

    Response (200):
      { "code": "123456", "valid_for": 30 }

    Response (500):
      { "error": "Seed not decrypted yet" }
    """
    # Check if seed file exists
    if not SEED_FILE.exists():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = SEED_FILE.read_text().strip()

        # Generate current TOTP code
        code = generate_totp_code(hex_seed)

        # Remaining seconds in current 30s period (0–29)
        now = int(time.time())
        valid_for = 30 - (now % 30)

        return {"code": code, "valid_for": valid_for}

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to generate 2FA code"},
        )


# ============
# Endpoint 3: POST /verify-2fa
# ============

@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    """
    POST /verify-2fa

    Request:
      { "code": "123456" }

    Response (200):
      { "valid": true } or { "valid": false }

    Response (400):
      { "error": "Missing code" }

    Response (500):
      { "error": "Seed not decrypted yet" }
    """
    # Validate that code is provided
    if body.code is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Missing code"},
        )

    # Check seed availability
    if not SEED_FILE.exists():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = SEED_FILE.read_text().strip()

        # Verify with ±1 period tolerance
        is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)

        return {"valid": is_valid}

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Verification failed"},
        )
