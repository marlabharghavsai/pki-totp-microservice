from pathlib import Path
import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_KEY_PATH = BASE_DIR / "student_public.pem"
ENCRYPTED_SEED_PATH = BASE_DIR / "encrypted_seed.txt"


def request_seed(student_id: str, github_repo_url: str, api_url: str = API_URL):
    """
    Request encrypted seed from instructor API
    """
    # 1. Read student public key from PEM file
    public_key_pem = PUBLIC_KEY_PATH.read_text()

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }

    # 3. Send POST request
    resp = requests.post(api_url, json=payload, timeout=15)
    resp.raise_for_status()

    # 4. Parse JSON response
    data = resp.json()
    if data.get("status") != "success":
        raise RuntimeError(f"Instructor API returned error: {data}")

    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        raise RuntimeError("No encrypted_seed found in response")

    # 5. Save encrypted seed to file
    ENCRYPTED_SEED_PATH.write_text(encrypted_seed.strip())

    print(f"✅ Encrypted seed saved to: {ENCRYPTED_SEED_PATH}")


def main():
    # 🔴 CHANGE THESE TWO VALUES 🔴
    student_id = "23P31A0503"
    github_repo_url = "https://github.com/marlabharghavsai/pki-totp-microservice"

    request_seed(student_id, github_repo_url)


if __name__ == "__main__":
    main()
