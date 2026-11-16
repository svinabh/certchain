"""Hashing helpers — the single place where cryptography lives.

Keeping all hashing in one file means a future hash upgrade touches
one module, and nothing else in the codebase knows the difference.
"""

import hashlib
import json
from typing import Any


def sha256_hex(text: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(payload: Any) -> str:
    """Serialize to a deterministic JSON string (same output on every machine/run).

    Deterministic serialization is what makes verification possible:
    identical block content must always produce the identical string to hash.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def hash_fields(fields: dict) -> str:
    """Hash the canonical JSON of a block's content fields."""
    return sha256_hex(canonical_json(fields))
