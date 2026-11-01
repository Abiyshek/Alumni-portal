"""
Audit Logging Module
Writes compliance-ready audit records.
"""

import os
import json
import hashlib
import logging
from datetime import datetime

from .config import LOCAL_OUTPUT_DIR, SENSITIVE_FIELDS

log = logging.getLogger("alumni_pipeline")


def write_audit_log(results: dict) -> None:
    """
    Writes a JSON audit record to LOCAL_OUTPUT_DIR (and in production to S3).
    Sensitive fields are hashed before logging.

    [IAM] Read access to this log should be restricted to the model-ops IAM role.
    """
    safe = {
        k: hashlib.sha256(str(v).encode()).hexdigest() if k in SENSITIVE_FIELDS else v
        for k, v in results.items()
    }
    safe["logged_at"] = datetime.now().isoformat()
    path = os.path.join(LOCAL_OUTPUT_DIR, "audit_log.json")
    with open(path, "w") as f:
        json.dump(safe, f, indent=2, default=str)
    log.info("  Audit log written → %s", path)
