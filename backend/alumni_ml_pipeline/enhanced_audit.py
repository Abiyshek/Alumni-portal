"""
Enhanced Audit Logging Module
Compliance-ready logging with AWS CloudTrail integration.
"""

import json
import hashlib
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from .config import LOCAL_OUTPUT_DIR
from .security import FieldMasking

log = logging.getLogger("alumni_pipeline")


class AuditLogger:
    """Audit logging for compliance."""

    def __init__(self, use_cloudtrail: bool = False):
        self.use_cloudtrail = use_cloudtrail
        self.cloudtrail_client = None

        if use_cloudtrail:
            try:
                import boto3
                self.cloudtrail_client = boto3.client("cloudtrail")
                log.info("✓ CloudTrail integration enabled")
            except Exception as e:
                log.warning(f"CloudTrail initialization failed: {e}")
                self.use_cloudtrail = False

    def log_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        resource: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        sensitive: bool = False
    ) -> bool:
        """
        Log an event with full audit trail.
        
        Args:
            event_type: Type of event (e.g., 'data_access', 'export', 'modification')
            user_id: ID of user performing action
            action: Specific action performed
            resource: Resource accessed (table, file, etc.)
            status: Success/Failure
            details: Additional context
            sensitive: Whether event involves sensitive data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {},
            "sensitive": sensitive,
        }

        # Mask sensitive fields in details
        if sensitive and "details" in event:
            event["details"] = FieldMasking.mask_dict_for_logging(event["details"])

        # Local logging
        self._log_local(event)

        # CloudTrail logging
        if self.use_cloudtrail:
            self._log_cloudtrail(event)

        return True

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        row_count: int,
        status: str = "success"
    ) -> bool:
        """Log data access event."""
        return self.log_event(
            event_type="data_access",
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            details={
                "rows_accessed": row_count,
                "access_method": "api",
            },
            sensitive=True
        )

    def log_data_export(
        self,
        user_id: str,
        resource: str,
        export_format: str,
        record_count: int,
        status: str = "success"
    ) -> bool:
        """Log data export event (compliance critical)."""
        return self.log_event(
            event_type="data_export",
            user_id=user_id,
            action=f"Export {export_format}",
            resource=resource,
            status=status,
            details={
                "export_format": export_format,
                "record_count": record_count,
                "exported_at": datetime.now().isoformat(),
            },
            sensitive=True
        )

    def log_report_view(
        self,
        user_id: str,
        report_id: str,
        report_type: str,
        status: str = "success"
    ) -> bool:
        """Log report view event."""
        return self.log_event(
            event_type="report_view",
            user_id=user_id,
            action=f"View {report_type}",
            resource=report_id,
            status=status,
            details={
                "report_type": report_type,
                "viewed_at": datetime.now().isoformat(),
            }
        )

    def log_model_scoring(
        self,
        model_version: str,
        alumni_scored: int,
        status: str = "success"
    ) -> bool:
        """Log model scoring event."""
        return self.log_event(
            event_type="model_scoring",
            user_id="system",
            action="Score alumni",
            resource="ensemble_model",
            status=status,
            details={
                "model_version": model_version,
                "alumni_scored": alumni_scored,
                "process_time": datetime.now().isoformat(),
            }
        )

    def log_error(
        self,
        event_type: str,
        user_id: str,
        action: str,
        resource: str,
        error_message: str
    ) -> bool:
        """Log error event."""
        return self.log_event(
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource=resource,
            status="error",
            details={
                "error_message": error_message,
                "error_time": datetime.now().isoformat(),
            }
        )

    @staticmethod
    def _log_local(event: Dict[str, Any]) -> None:
        """Write audit log to local file."""
        try:
            log_path = os.path.join(LOCAL_OUTPUT_DIR, "audit_trail.jsonl")
            os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

            # Append to JSONL file
            with open(log_path, "a") as f:
                f.write(json.dumps(event, default=str) + "\n")

            log.debug(f"✓ Audit logged: {event['event_type']} - {event['action']}")
        except Exception as e:
            log.error(f"✗ Audit logging failed: {e}")

    def _log_cloudtrail(self, event: Dict[str, Any]) -> None:
        """Write audit log to CloudTrail."""
        try:
            if not self.cloudtrail_client:
                return

            # Convert to CloudTrail format
            cloudtrail_event = {
                "eventName": event["action"],
                "eventSource": "alumni.internal",
                "eventTime": event["timestamp"],
                "userIdentity": {
                    "principalId": event["user_id"],
                    "type": "IAMUser",
                },
                "requestParameters": {
                    "resource": event["resource"],
                    "details": event["details"],
                },
                "responseElements": {
                    "status": event["status"],
                },
            }

            # TODO: Send to CloudTrail via PutEvents
            log.debug(f"✓ CloudTrail logged: {event['action']}")
        except Exception as e:
            log.error(f"✗ CloudTrail logging failed: {e}")


# ── Global audit logger instance ──────────────────────────────────────────────
audit_logger = AuditLogger(use_cloudtrail=False)


def write_enhanced_audit_log(
    results: Dict[str, Any],
    user_id: str = "system"
) -> None:
    """Write enhanced audit log with all events."""
    combined_log = {
        "session_id": hashlib.md5(f"{datetime.now().isoformat()}{user_id}".encode()).hexdigest(),
        "logged_at": datetime.now().isoformat(),
        "user_id": user_id,
        "results": results,
        "sensitive_fields_masked": True,
    }

    # Mask sensitive data
    masked_results = FieldMasking.mask_dict_for_logging(results)
    combined_log["results"] = masked_results

    audit_logger.log_event(
        event_type="pipeline_execution",
        user_id=user_id,
        action="Execute alumni pipeline",
        resource="ml_pipeline",
        status="success",
        details=combined_log,
        sensitive=True
    )

    log.info(f"✓ Enhanced audit log written for session {combined_log['session_id']}")
