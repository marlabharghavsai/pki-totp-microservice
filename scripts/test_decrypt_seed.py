import sys
from pathlib import Path

# ✅ Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.crypto_utils import load_student_private_key, decrypt_seed


ENCRYPTED_SEED_PATH = BASE_DIR / "encrypted_seed.txt"


def main():
    private_key = load_student_private_key()
    encrypted_seed_b64 = ENCRYPTED_SEED_PATH.read_text().strip()

    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    print("Decrypted seed:", hex_seed)
    print("Length:", len(hex_seed))


if __name__ == "__main__":
    main()
