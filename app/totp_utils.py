import base64
import pyotp


def _hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to Base32 string
    (required by the TOTP library).
    """
    # 1. Hex string -> bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. Bytes -> Base32 text
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.

    Args:
        hex_seed: 64-character hex string

    Returns:
        6-digit TOTP code as string, e.g. "123456".
    """
    # 1 & 2. Hex -> bytes -> Base32
    base32_seed = _hex_to_base32(hex_seed)

    # 3. Create TOTP object
    totp = pyotp.TOTP(
        base32_seed,
        interval=30,  # 30-second period
        digits=6      # 6-digit codes
        # SHA-1 is default
    )

    # 4 & 5. Generate and return code
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance.

    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: Number of periods before/after to accept (default 1 = ±30s)

    Returns:
        True if code is valid, False otherwise.
    """
    # 1. Hex -> Base32 (same as generation)
    base32_seed = _hex_to_base32(hex_seed)

    # 2. Create TOTP object
    totp = pyotp.TOTP(
        base32_seed,
        interval=30,
        digits=6
    )

    # 3 & 4. Verify with ±valid_window periods (±30s by default)
    return totp.verify(code, valid_window=valid_window)
