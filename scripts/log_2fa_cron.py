#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime, timezone

# Make sure project root is on path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.totp_utils import generate_totp_code

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"


def main():
    if not SEED_FILE.exists():
        print("Seed file not found at /data/seed.txt", file=sys.stderr)
        return

    hex_seed = SEED_FILE.read_text().strip()

    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        print(f"Error generating TOTP code: {e}", file=sys.stderr)
        return

    now_utc = datetime.now(timezone.utc)
    ts = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - 2FA Code: {code}")


if __name__ == "__main__":
    main()
