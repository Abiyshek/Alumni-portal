"""
Global configuration constants for the alumni pipeline.
"""

from datetime import datetime

# ── Global constants ──────────────────────────────────────────────────────────
CURRENT_YEAR      = datetime.now().year
RANDOM_SEED       = 42
TEST_SIZE         = 0.2
CV_FOLDS          = 5
ENSEMBLE_W_XGB    = 0.55   # weight for XGBoost in ensemble
ENSEMBLE_W_CAT    = 0.45   # weight for CatBoost in ensemble
TARGET_COL        = "will_donate"          # binary label we predict

# ── AWS / S3 path stubs (swap to real s3:// URIs in production) ───────────────
S3_INPUT_PREFIX   = "s3://alumni-data-lake/raw/"
S3_OUTPUT_PREFIX  = "s3://alumni-data-lake/scores/"
S3_MODEL_PREFIX   = "s3://alumni-data-lake/models/"

# ── Kaggle local paths (used when S3 is not available) ───────────────────────
LOCAL_INPUT_DIR   = "G:/MINI_PROJECT/dataset/"
LOCAL_OUTPUT_DIR  = "G:/MINI_PROJECT/output/"

# ── Sensitive field list (masked in audit logs) ───────────────────────────────
SENSITIVE_FIELDS  = ["donation_amount", "total_donations", "email", "phone", "LINK"]

# ── Feature columns for model input ───────────────────────────────────────────
FEATURE_COLS = [
    # Mandatory engineered features
    "years_since_graduation",
    "event_attendance_count",
    "newsletter_interaction_score",
    "portal_login_frequency",
    "donation_recency",
    "total_donation_amount",
    "engagement_score",
    "donation_affinity_score",
    # Derived extras
    "seniority_level",
    "degree_numeric",
    "proximity_score",
    "is_mid_career",
    "gpa_avg",
]
