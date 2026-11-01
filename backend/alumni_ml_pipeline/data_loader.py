"""
Data Loader Module
Abstracts data ingestion from either S3 (production) or local filesystem.
"""

import os
import logging
from typing import Dict, Optional

import pandas as pd

from .config import LOCAL_INPUT_DIR, S3_INPUT_PREFIX

log = logging.getLogger("alumni_pipeline")


class DataLoader:
    """
    Abstracts data ingestion from either S3 (production) or local filesystem
    (development / Kaggle).  In production, replace _read_local with a
    boto3 / awswrangler call that reads from S3 and writes via Glue/Spark.

    IAM note [IAM]: The IAM role attached to the SageMaker Processing Job must
    have  s3:GetObject  on the input bucket and  s3:PutObject  on the output
    bucket.  No credentials are hard-coded here.
    """

    ENCODINGS = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]

    FILES = {
        "alumni_people"   : "alumni_people_from_departmant.csv",
        "work_locations"  : "where_they_work.csv",
        "genders"         : "genders.csv",
        "cities"          : "cities.csv",
        "geographic_area" : "geographic_area.csv",
        "colleges_cs"     : "colleges_computerscience.csv",
        "college_scores"  : "college_scores.csv",
        "departments"     : "college_departmans.csv",
        "lectures"        : "computer_science_lectures.csv",
        "student_scores"  : "best_students_lecture_scores.csv",
        "academics"       : "academics.csv",
    }

    def __init__(self, use_s3: bool = False, local_dir: str = LOCAL_INPUT_DIR):
        self.use_s3    = use_s3
        self.local_dir = local_dir
        self.raw       : Dict[str, pd.DataFrame] = {}

    # ── public ────────────────────────────────────────────────────────────────
    def load_all(self) -> Dict[str, pd.DataFrame]:
        log.info("=== DATA LOADING ===")
        for name, filename in self.FILES.items():
            df = self._load_one(filename)
            if df is not None:
                self.raw[name] = df
                log.info("  ✓ %-20s  rows=%-5d  cols=%d", name, len(df), df.shape[1])
            else:
                log.warning("  ✗ %-20s  FAILED", name)
        log.info("  Loaded %d / %d files", len(self.raw), len(self.FILES))
        return self.raw

    # ── private ───────────────────────────────────────────────────────────────
    def _load_one(self, filename: str) -> Optional[pd.DataFrame]:
        if self.use_s3:
            return self._read_s3(filename)
        return self._read_local(filename)

    def _read_local(self, filename: str) -> Optional[pd.DataFrame]:
        path = os.path.join(self.local_dir, filename)
        for enc in self.ENCODINGS:
            try:
                return pd.read_csv(path, encoding=enc)
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                log.warning("    File not found: %s", path)
                return None
        return None

    def _read_s3(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Production stub — replace body with:
            import awswrangler as wr
            return wr.s3.read_csv(S3_INPUT_PREFIX + filename)
        [IAM] Requires s3:GetObject on the source bucket.
        """
        log.info("  [S3] Would read: %s%s", S3_INPUT_PREFIX, filename)
        return self._read_local(filename)  # fallback to local for now
