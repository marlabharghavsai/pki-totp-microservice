import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.crypto_utils import load_student_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, verify_totp_code

ENCRYPTED_SEED_PATH = BASE_DIR / "encrypted_seed.txt"


def main():
    private_key = load_student_private_key()
    encrypted_seed_b64 = ENCRYPTED_SEED_PATH.read_text().strip()
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    code = generate_totp_code(hex_seed)
    print("Code:", code)

    ok = verify_totp_code(hex_seed, code, valid_window=1)
    print("Valid:", ok)


if __name__ == "__main__":
    main()
