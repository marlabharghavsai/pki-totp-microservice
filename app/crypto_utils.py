from pathlib import Path
import base64

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


BASE_DIR = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "student_private.pem"


def load_student_private_key():
    """
    Load the student RSA private key from student_private.pem
    and return it as a key object.
    """
    pem_data = PRIVATE_KEY_PATH.read_bytes()
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # key is not encrypted
    )
    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext
        private_key: RSA private key object

    Returns:
        Decrypted hex seed (64-character string)

    Implementation:
    1. Base64 decode the encrypted seed string
    2. RSA/OAEP decrypt with SHA-256
       - Padding: OAEP
       - MGF: MGF1(SHA-256)
       - Hash: SHA-256
       - Label: None
    3. Decode bytes to UTF-8 string
    4. Validate: must be 64-character hex string
       - Check length is 64
       - Check all characters are in '0123456789abcdef'
    5. Return hex seed
    """
    # 1. Base64 decode
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt with SHA-256 + MGF1(SHA-256) + label=None
    plaintext_bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # 3. Decode bytes to UTF-8 string
    seed = plaintext_bytes.decode("utf-8").strip()

    # 4. Validate 64-char lowercase hex
    if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        raise ValueError(f"Invalid seed format: {seed!r}")

    # 5. Return hex seed
    return seed
