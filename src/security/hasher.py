"""
ATTACHORA Hasher Module
Computes cryptographic SHA-256 hashes for attachment integrity and deduplication.
"""

import hashlib
from pathlib import Path
from typing import BinaryIO, Union


def calculate_sha256(data_or_path: Union[bytes, str, Path, BinaryIO]) -> str:
    """Calculates SHA-256 hash in hexadecimal string from bytes, file path, or stream."""
    sha = hashlib.sha256()

    if isinstance(data_or_path, bytes):
        sha.update(data_or_path)
        return sha.hexdigest().lower()

    if isinstance(data_or_path, (str, Path)):
        path = Path(data_or_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found for hash computation: {path}")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest().lower()

    if hasattr(data_or_path, "read"):
        for chunk in iter(lambda: data_or_path.read(65536), b""):
            sha.update(chunk)
        return sha.hexdigest().lower()

    raise ValueError("Unsupported input type for calculate_sha256")
