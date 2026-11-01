"""
S3 Data Storage Module
Handles reading/writing data to AWS S3.
"""

import logging
import json
import os
import pandas as pd
from typing import Optional, Dict, Any, List

log = logging.getLogger("alumni_pipeline")

try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    log.warning("boto3 not installed — S3 integration disabled")


class S3DataStore:
    """Interface for S3 data operations."""

    def __init__(self, bucket: str, region: str = "us-east-1", use_local: bool = False):
        """
        Initialize S3 data store.
        
        Args:
            bucket: S3 bucket name
            region: AWS region
            use_local: Use local directory instead (for testing)
        """
        self.bucket = bucket
        self.region = region
        self.use_local = use_local
        self.s3_client = None
        self.local_dir = None

        if not use_local and S3_AVAILABLE:
            try:
                self.s3_client = boto3.client("s3", region_name=region)
                log.info(f"✓ S3 client initialized: {bucket}")
            except Exception as e:
                log.warning(f"S3 initialization failed: {e}. Falling back to local storage.")
                self.use_local = True
        
        if use_local:
            self.local_dir = f"./s3_local/{bucket}"
            os.makedirs(self.local_dir, exist_ok=True)
            log.info(f"✓ Local storage initialized: {self.local_dir}")

    def put_object(self, key: str, body: bytes, metadata: Optional[Dict] = None) -> bool:
        """Upload object to S3."""
        try:
            if self.use_local:
                return self._put_local(key, body)
            else:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=body,
                    Metadata=metadata or {}
                )
                log.info(f"✓ Uploaded to S3: s3://{self.bucket}/{key}")
                return True
        except Exception as e:
            log.error(f"✗ S3 upload failed: {e}")
            return False

    def get_object(self, key: str) -> Optional[bytes]:
        """Download object from S3."""
        try:
            if self.use_local:
                return self._get_local(key)
            else:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
                return response["Body"].read()
        except Exception as e:
            log.error(f"✗ S3 download failed: {e}")
            return None

    def put_csv(self, key: str, df: pd.DataFrame) -> bool:
        """Upload DataFrame as CSV to S3."""
        try:
            csv_body = df.to_csv(index=False).encode("utf-8")
            return self.put_object(key, csv_body, {"content-type": "text/csv"})
        except Exception as e:
            log.error(f"✗ CSV upload failed: {e}")
            return False

    def get_csv(self, key: str) -> Optional[pd.DataFrame]:
        """Download CSV from S3 as DataFrame."""
        try:
            body = self.get_object(key)
            if body:
                return pd.read_csv(pd.io.common.BytesIO(body))
        except Exception as e:
            log.error(f"✗ CSV download failed: {e}")
        return None

    def put_json(self, key: str, data: Dict[str, Any]) -> bool:
        """Upload JSON to S3."""
        try:
            json_body = json.dumps(data, default=str).encode("utf-8")
            return self.put_object(key, json_body, {"content-type": "application/json"})
        except Exception as e:
            log.error(f"✗ JSON upload failed: {e}")
            return False

    def get_json(self, key: str) -> Optional[Dict]:
        """Download JSON from S3."""
        try:
            body = self.get_object(key)
            if body:
                return json.loads(body.decode("utf-8"))
        except Exception as e:
            log.error(f"✗ JSON download failed: {e}")
        return None

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> List[str]:
        """List objects in S3 bucket."""
        try:
            if self.use_local:
                return self._list_local(prefix)
            else:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=prefix,
                    MaxKeys=max_keys
                )
                return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            log.error(f"✗ List failed: {e}")
            return []

    def delete_object(self, key: str) -> bool:
        """Delete object from S3."""
        try:
            if self.use_local:
                return self._delete_local(key)
            else:
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                log.info(f"✓ Deleted from S3: s3://{self.bucket}/{key}")
                return True
        except Exception as e:
            log.error(f"✗ Delete failed: {e}")
            return False

    # ── Local file operations (fallback) ───────────────────────────────────────
    def _put_local(self, key: str, body: bytes) -> bool:
        """Save to local file."""
        try:
            file_path = os.path.join(self.local_dir, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(body)
            log.info(f"✓ Saved locally: {file_path}")
            return True
        except Exception as e:
            log.error(f"✗ Local save failed: {e}")
            return False

    def _get_local(self, key: str) -> Optional[bytes]:
        """Read from local file."""
        try:
            file_path = os.path.join(self.local_dir, key)
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            log.error(f"✗ Local read failed: {e}")
            return None

    def _list_local(self, prefix: str = "") -> List[str]:
        """List local files."""
        try:
            prefix_path = os.path.join(self.local_dir, prefix)
            files = []
            for root, dirs, filenames in os.walk(prefix_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), self.local_dir)
                    files.append(rel_path.replace("\\", "/"))
            return files
        except Exception as e:
            log.error(f"✗ Local list failed: {e}")
            return []

    def _delete_local(self, key: str) -> bool:
        """Delete local file."""
        try:
            file_path = os.path.join(self.local_dir, key)
            if os.path.exists(file_path):
                os.remove(file_path)
                log.info(f"✓ Deleted locally: {file_path}")
            return True
        except Exception as e:
            log.error(f"✗ Local delete failed: {e}")
            return False


# ── Convenience functions ─────────────────────────────────────────────────────

def get_s3_store(bucket: str, use_local: bool = True) -> S3DataStore:
    """Get configured S3 data store."""
    return S3DataStore(bucket, use_local=use_local)


def upload_file_to_s3(file_path: str, s3_key: str, bucket: str) -> bool:
    """Upload a local file to S3."""
    try:
        with open(file_path, "rb") as f:
            body = f.read()
        store = S3DataStore(bucket)
        return store.put_object(s3_key, body)
    except Exception as e:
        log.error(f"✗ File upload failed: {e}")
        return False


def download_file_from_s3(s3_key: str, bucket: str, local_path: str) -> bool:
    """Download a file from S3 to local filesystem."""
    try:
        store = S3DataStore(bucket)
        body = store.get_object(s3_key)
        if body:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(body)
            log.info(f"✓ Downloaded to: {local_path}")
            return True
        return False
    except Exception as e:
        log.error(f"✗ File download failed: {e}")
        return False
