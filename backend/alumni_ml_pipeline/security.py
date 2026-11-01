"""
Data Encryption & Security Module
Handles encryption/decryption of sensitive fields using AWS KMS.
"""

import logging
import json
from typing import Dict, Any

log = logging.getLogger("alumni_pipeline")

SENSITIVE_FIELDS = [
    "donation_amount",
    "total_donations",
    "email",
    "phone",
    "ssn",
    "address",
    "credit_card",
]


class DataEncryption:
    """
    Encrypts and decrypts sensitive data fields using KMS or local encryption.
    In production: Uses AWS KMS for key management and encryption.
    In development: Uses simple base64 encoding (not secure).
    """

    def __init__(self, use_kms: bool = False, kms_key_id: str = None):
        self.use_kms = use_kms
        self.kms_key_id = kms_key_id
        self.kms_client = None

        if use_kms:
            try:
                import boto3
                self.kms_client = boto3.client("kms")
                log.info("✓ KMS encryption enabled")
            except Exception as e:
                log.warning(f"KMS initialization failed: {e}. Using local encryption.")
                self.use_kms = False

    def encrypt_field(self, value: Any) -> str:
        """Encrypt a single field value."""
        if value is None:
            return None

        plain_text = str(value).encode("utf-8")

        if self.use_kms and self.kms_client:
            try:
                response = self.kms_client.encrypt(
                    KeyId=self.kms_key_id,
                    Plaintext=plain_text
                )
                # Return base64-encoded ciphertext
                import base64
                return base64.b64encode(response["CiphertextBlob"]).decode("utf-8")
            except Exception as e:
                log.error(f"KMS encryption failed: {e}")
                return self._local_encrypt(plain_text)
        else:
            return self._local_encrypt(plain_text)

    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a single field value."""
        if encrypted_value is None:
            return None

        if self.use_kms and self.kms_client:
            try:
                import base64
                ciphertext = base64.b64decode(encrypted_value)
                response = self.kms_client.decrypt(CiphertextBlob=ciphertext)
                return response["Plaintext"].decode("utf-8")
            except Exception as e:
                log.error(f"KMS decryption failed: {e}")
                return self._local_decrypt(encrypted_value)
        else:
            return self._local_decrypt(encrypted_value)

    def encrypt_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt all sensitive fields in a row."""
        encrypted = row.copy()
        for field in SENSITIVE_FIELDS:
            if field in encrypted and encrypted[field] is not None:
                encrypted[field] = self.encrypt_field(encrypted[field])
        return encrypted

    def decrypt_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt all sensitive fields in a row."""
        decrypted = row.copy()
        for field in SENSITIVE_FIELDS:
            if field in decrypted and decrypted[field] is not None:
                decrypted[field] = self.decrypt_field(decrypted[field])
        return decrypted

    @staticmethod
    def _local_encrypt(plain_bytes: bytes) -> str:
        """Local encryption (development only - NOT SECURE)."""
        import base64
        return base64.b64encode(plain_bytes).decode("utf-8")

    @staticmethod
    def _local_decrypt(encrypted_str: str) -> str:
        """Local decryption (development only - NOT SECURE)."""
        import base64
        return base64.b64decode(encrypted_str.encode("utf-8")).decode("utf-8")


class FieldMasking:
    """Masks sensitive fields for display/logging."""

    @staticmethod
    def mask_field(value: Any, field_name: str, mask_char: str = "*") -> str:
        """Mask a sensitive field value."""
        if value is None:
            return None

        value_str = str(value)

        if field_name == "email":
            parts = value_str.split("@")
            if len(parts) == 2:
                return f"{parts[0][0]}***@{parts[1]}"
            return f"{mask_char * len(value_str)}"

        elif field_name == "phone":
            return f"{mask_char * 6}{value_str[-4:]}"

        elif field_name in ["ssn", "credit_card"]:
            return f"{mask_char * (len(value_str) - 4)}{value_str[-4:]}"

        elif field_name in ["donation_amount", "total_donations"]:
            return f"${mask_char * 5}"

        else:
            return f"{mask_char * len(value_str)}"

    @staticmethod
    def mask_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Mask all sensitive fields in a row."""
        masked = row.copy()
        for field in SENSITIVE_FIELDS:
            if field in masked and masked[field] is not None:
                masked[field] = FieldMasking.mask_field(masked[field], field)
        return masked

    @staticmethod
    def mask_dict_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in a dictionary for safe logging."""
        safe_data = data.copy()
        for field in SENSITIVE_FIELDS:
            if field in safe_data:
                safe_data[field] = FieldMasking.mask_field(safe_data[field], field)
        return safe_data
