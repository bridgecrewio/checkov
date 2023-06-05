from __future__ import annotations

import hashlib
from pathlib import Path


def hash_file_content(content: bytes) -> str:
    sha256 = hashlib.sha256(content)
    return sha256.hexdigest()


def hash_file(file_path: str | Path) -> str:
    return hash_file_content(Path(file_path).read_bytes())
