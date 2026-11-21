"""
ATTACHORA Credential Vault
Provides encrypted local credential storage, in-memory runtime secrets management,
and credential masking to prevent plaintext exposure.
"""

import base64
import hashlib
import hmac
import os
from pathlib import Path
import platform
import secrets
from typing import Dict, Optional
from src.config import CONFIG


class CredentialVault:
    def __init__(self, key_path: Optional[Path] = None):
        self.key_path = Path(key_path or CONFIG.VAULT_KEY_PATH)
        self._memory_vault: Dict[str, str] = {}
        self._master_key = self._get_or_create_master_key()

    def _get_or_create_master_key(self) -> bytes:
        """Derives or generates a machine-bound master key for local encryption."""
        if self.key_path.exists():
            try:
                with open(self.key_path, "rb") as f:
                    return f.read().strip()
            except Exception:
                pass

        # Generate a high-entropy 256-bit key combined with machine fingerprint
        node_id = platform.node().encode("utf-8")
        random_bytes = secrets.token_bytes(32)
        derived = hashlib.pbkdf2_hmac("sha256", random_bytes, node_id, 100_000, 32)
        key_b64 = base64.urlsafe_b64encode(derived)

        try:
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_path, "wb") as f:
                f.write(key_b64)
        except Exception:
            # Fall back to ephemeral in-memory master key if write restricted
            pass

        return key_b64

    def _xor_cipher(self, data: bytes, key: bytes) -> bytes:
        """Symmetric stream cipher utilizing HMAC-SHA256 keystream."""
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(data):
            block = hmac.new(key, counter.to_bytes(4, "big"), hashlib.sha256).digest()
            keystream.extend(block)
            counter += 1
        return bytes(a ^ b for a, b in zip(data, keystream[: len(data)]))

    def encrypt_secret(self, plaintext: str) -> str:
        """Encrypts a plaintext secret into an armored base64 token."""
        if not plaintext:
            return ""
        nonce = secrets.token_bytes(16)
        key = hashlib.sha256(self._master_key + nonce).digest()
        cipher_bytes = self._xor_cipher(plaintext.encode("utf-8"), key)
        # Prepend nonce
        payload = nonce + cipher_bytes
        # Add HMAC tag for authentication (prevent tampering)
        tag = hmac.new(key, payload, hashlib.sha256).digest()[:16]
        return base64.urlsafe_b64encode(tag + payload).decode("ascii")

    def decrypt_secret(self, token: str) -> Optional[str]:
        """Decrypts an encrypted token.

        Returns None if tampered or invalid.
        """
        if not token:
            return None
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii"))
            tag = raw[:16]
            payload = raw[16:]
            nonce = payload[:16]
            cipher_bytes = payload[16:]

            key = hashlib.sha256(self._master_key + nonce).digest()
            expected_tag = hmac.new(key, payload, hashlib.sha256).digest()[:16]
            if not hmac.compare_digest(tag, expected_tag):
                return None  # Integrity verification failed

            plaintext_bytes = self._xor_cipher(cipher_bytes, key)
            return plaintext_bytes.decode("utf-8")
        except Exception:
            return None

    def set_memory_credential(self, account_email: str, password_or_token: str) -> None:
        """Stores a credential only in volatile RAM for the active session."""
        self._memory_vault[account_email.lower()] = password_or_token

    def get_memory_credential(self, account_email: str) -> Optional[str]:
        """Retrieves an in-memory session credential."""
        return self._memory_vault.get(account_email.lower())

    def clear_memory_vault(self) -> None:
        self._memory_vault.clear()


def mask_credential(secret: Optional[str]) -> str:
    """Masks a sensitive credential for display."""
    if not secret:
        return "(none)"
    return "••••••••"


# Global credential vault instance
VAULT = CredentialVault()
