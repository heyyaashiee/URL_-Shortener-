"""
Short-code generation logic (Step 2 of the roadmap).

Approach: generate a random base62 string (letters + digits) of a given
length, then check the database to make sure it's not already in use.
Retry with a fresh code on the rare occasion of a collision.

Why base62?
- Uses [0-9a-zA-Z] = 62 characters, all URL-safe (no encoding needed).
- 6 characters of base62 gives 62^6 ≈ 56.8 billion possible codes --
  more than enough for a learning project, and the same idea scales
  to real systems (just increase length or switch to an ID-based scheme).
"""

import secrets
import string
from sqlalchemy.orm import Session

from app import models

ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9 (62 chars)
DEFAULT_CODE_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 5


def _random_base62(length: int) -> str:
    """Generate one random base62 string of the given length."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_short_code(db: Session, length: int = DEFAULT_CODE_LENGTH) -> str:
    """
    Generate a short code guaranteed not to collide with an existing one
    in the database. Retries a few times before giving up (extremely
    unlikely to ever be needed at this code length, but good practice).
    """
    for _ in range(MAX_GENERATION_ATTEMPTS):
        code = _random_base62(length)
        exists = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not exists:
            return code

    # Collisions this many times in a row is astronomically unlikely --
    # if it happens, bump the length rather than looping forever.
    raise RuntimeError(
        f"Could not generate a unique short code after {MAX_GENERATION_ATTEMPTS} attempts. "
        "Consider increasing DEFAULT_CODE_LENGTH."
    )
