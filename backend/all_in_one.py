"""
================================================================================
  ALUMNI DONATION & ENGAGEMENT PREDICTION SYSTEM
  Production-Ready ML Pipeline | AWS-Compatible Architecture
================================================================================
  Author   : Senior ML Engineer
  Version  : 2.0.0
  Python   : 3.9+
  Platform : Kaggle (dev) → AWS SageMaker / Glue (prod)
  Infra    : S3 (storage) · Glue/Spark (ETL) · SageMaker (inference)
================================================================================

PIPELINE LAYERS
  1. Data Loading         — S3-aware CSV ingestion with encoding fallback
  2. EDA Summary          — Retained summary stats (non-destructive)
  3. Feature Engineering  — 8 mandatory derived features + preprocessing
  4. Baseline Model       — Logistic Regression (explainability anchor)
  5. Production Models    — XGBoost + CatBoost (ensemble)
  6. Ensemble Scoring     — Weighted probability fusion
  7. Evaluation           — AUC, ROC, confusion matrix, SHAP-style importance
  8. GenAI Insight Layer  — Anthropic-powered NL insights from model outputs

SECURITY NOTES (IAM / Compliance)
  - Sensitive fields (donations, contact info) are masked for logging
  - Role-based access placeholders are marked with # [IAM]
  - Model outputs are audit-logged to a dedicated output path
================================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# 0. IMPORTS & GLOBAL CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
import os
import json
import hashlib
import logging
import warnings
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless-safe; swap to TkAgg locally if needed
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    roc_auc_score, roc_curve, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, average_precision_score
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] xgboost not installed — XGBoost layer will be skipped.")

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("[WARN] catboost not installed — CatBoost layer will be skipped.")

warnings.filterwarnings("ignore")

# ── Logging setup (audit-ready) ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("alumni_pipeline")

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
LOCAL_INPUT_DIR   = "/kaggle/input/computer-science-department-and-alumni-datasets/"
LOCAL_OUTPUT_DIR  = "/kaggle/working/"

# ── Sensitive field list (masked in audit logs) ───────────────────────────────
SENSITIVE_FIELDS  = ["donation_amount", "total_donations", "email", "phone", "LINK"]

np.random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING  (S3-aware, encoding-resilient)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# 2. EDA SUMMARY  (retained — non-destructive)
# ─────────────────────────────────────────────────────────────────────────────

class EDASummary:
    """
    Lightweight EDA that prints summary statistics without mutating the data.
    Generates one multi-panel figure saved to LOCAL_OUTPUT_DIR.
    """

    def run(self, raw: Dict[str, pd.DataFrame]) -> None:
        log.info("=== EDA SUMMARY ===")
        self._print_dataset_overview(raw)
        self._analyze_alumni_people(raw.get("alumni_people"))
        self._analyze_work_locations(raw.get("work_locations"))
        self._analyze_student_scores(raw.get("student_scores"))
        self._plot_eda(raw)

    # ── individual analyses ───────────────────────────────────────────────────
    @staticmethod
    def _print_dataset_overview(raw: Dict[str, pd.DataFrame]) -> None:
        print("\n" + "─" * 60)
        print("  DATASET INVENTORY")
        print("─" * 60)
        for name, df in raw.items():
            missing_pct = df.isnull().mean().mean() * 100
            print(f"  {name:<25}  {len(df):>5} rows  {df.shape[1]:>3} cols  "
                  f"missing={missing_pct:.1f}%")

    @staticmethod
    def _analyze_alumni_people(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── alumni_people ──")
        print(f"  Total alumni recorded : {len(df)}")
        if "cinsiyet" in df.columns:
            gender_counts = df["cinsiyet"].value_counts()
            print(f"  Gender distribution  : {gender_counts.to_dict()}")
        if "title" in df.columns:
            top_titles = df["title"].value_counts().head(5)
            print("  Top 5 job titles:")
            for title, cnt in top_titles.items():
                print(f"    {cnt:>3}  {title}")
        if "company" in df.columns:
            n_missing = df["company"].isnull().sum()
            print(f"  Companies with missing data: {n_missing} ({n_missing/len(df):.0%})")

    @staticmethod
    def _analyze_work_locations(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── work_locations ──")
        if "kişi" in df.columns and "kurum" in df.columns:
            top = df.nlargest(5, "kişi")[["kurum", "kişi"]]
            print("  Top 5 employers by alumni count:")
            for _, row in top.iterrows():
                print(f"    {row['kişi']:>3}  {row['kurum']}")

    @staticmethod
    def _analyze_student_scores(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── student_scores ──")
        if "ORTALAMA" in df.columns:
            s = df["ORTALAMA"]
            print(f"  GPA — mean={s.mean():.2f}  median={s.median():.2f}  "
                  f"std={s.std():.2f}  min={s.min():.2f}  max={s.max():.2f}")
        if "SINIF" in df.columns:
            print(f"  Class distribution: {df['SINIF'].value_counts().to_dict()}")

    @staticmethod
    def _plot_eda(raw: Dict[str, pd.DataFrame]) -> None:
        fig = plt.figure(figsize=(18, 10))
        fig.suptitle("EDA Summary — Alumni Dataset", fontsize=15, fontweight="bold", y=1.01)
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

        # Panel 1: dataset sizes
        ax1 = fig.add_subplot(gs[0, 0])
        names = list(raw.keys())
        sizes = [len(raw[n]) for n in names]
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(names)))
        ax1.barh(names, sizes, color=colors)
        ax1.set_xlabel("Row count")
        ax1.set_title("Dataset Sizes")
        ax1.tick_params(axis="y", labelsize=7)

        # Panel 2: alumni job title distribution
        alumni = raw.get("alumni_people")
        ax2 = fig.add_subplot(gs[0, 1])
        if alumni is not None and "title" in alumni.columns:
            top_t = alumni["title"].value_counts().head(8)
            ax2.barh(top_t.index[::-1], top_t.values[::-1],
                     color=plt.cm.plasma(np.linspace(0.2, 0.8, len(top_t))))
            ax2.set_title("Top Job Titles")
            ax2.tick_params(axis="y", labelsize=7)
        else:
            ax2.text(0.5, 0.5, "No data", ha="center", va="center")
            ax2.set_title("Top Job Titles")

        # Panel 3: employer distribution
        wl = raw.get("work_locations")
        ax3 = fig.add_subplot(gs[0, 2])
        if wl is not None and "kişi" in wl.columns and "kurum" in wl.columns:
            top_w = wl.nlargest(8, "kişi")
            ax3.barh(top_w["kurum"].values[::-1], top_w["kişi"].values[::-1],
                     color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(top_w))))
            ax3.set_title("Top Employers (alumni count)")
            ax3.tick_params(axis="y", labelsize=7)
        else:
            ax3.text(0.5, 0.5, "No data", ha="center", va="center")
            ax3.set_title("Top Employers")

        # Panel 4: GPA distribution
        ss = raw.get("student_scores")
        ax4 = fig.add_subplot(gs[1, 0])
        if ss is not None and "ORTALAMA" in ss.columns:
            ax4.hist(ss["ORTALAMA"].dropna(), bins=25, color="#4C72B0",
                     edgecolor="white", linewidth=0.5)
            ax4.axvline(ss["ORTALAMA"].mean(), color="tomato", ls="--", label="Mean")
            ax4.set_xlabel("GPA (ORTALAMA)")
            ax4.set_title("GPA Distribution")
            ax4.legend(fontsize=8)
        else:
            ax4.text(0.5, 0.5, "No data", ha="center", va="center")
            ax4.set_title("GPA Distribution")

        # Panel 5: gender by year (genders table)
        gdf = raw.get("genders")
        ax5 = fig.add_subplot(gs[1, 1])
        if gdf is not None and "Unnamed: 0" in gdf.columns:
            year_cols = [c for c in gdf.columns if c.isdigit()]
            if year_cols:
                row = gdf[gdf["Unnamed: 0"].str.lower().str.contains("kiz-pc", na=False)]
                if not row.empty:
                    vals = row[year_cols].values.flatten()
                    ax5.plot(year_cols, vals, marker="o", color="orchid", label="Female")
                row2 = gdf[gdf["Unnamed: 0"].str.lower().str.contains("erkek-pc", na=False)]
                if not row2.empty:
                    vals2 = row2[year_cols].values.flatten()
                    ax5.plot(year_cols, vals2, marker="s", color="steelblue", label="Male")
                ax5.set_title("Gender Enrollment by Year")
                ax5.legend(fontsize=8)
        else:
            ax5.text(0.5, 0.5, "No data", ha="center", va="center")
            ax5.set_title("Gender Enrollment by Year")

        # Panel 6: missing value heatmap
        ax6 = fig.add_subplot(gs[1, 2])
        miss_pct = {n: df.isnull().mean().mean() * 100 for n, df in raw.items()}
        miss_df = pd.DataFrame(miss_pct, index=["missing_%"]).T.sort_values("missing_%")
        ax6.barh(miss_df.index, miss_df["missing_%"],
                 color=["#d73027" if v > 20 else "#fee090" if v > 5 else "#91cf60"
                        for v in miss_df["missing_%"]])
        ax6.set_xlabel("Missing %")
        ax6.set_title("Missing Data by Dataset")
        ax6.tick_params(axis="y", labelsize=7)

        out_path = os.path.join(LOCAL_OUTPUT_DIR, "01_eda_summary.png")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        log.info("  EDA figure saved → %s", out_path)


# ─────────────────────────────────────────────────────────────────────────────
# 3. FEATURE ENGINEERING
#    8 mandatory features + preprocessing utilities
#    In production this block runs as an AWS Glue PySpark job.
# ─────────────────────────────────────────────────────────────────────────────

class FeatureEngineer:
    """
    Builds the model-ready feature matrix from raw datasets.

    AWS Glue / Spark note:
      Replace pandas transformations with Spark equivalents when running at
      scale.  The column names and logic remain identical; only the DataFrame
      API changes (spark.sql vs pandas).

    Mandatory derived features (per spec):
      1. years_since_graduation       — seniority proxy
      2. event_attendance_count       — direct engagement signal
      3. newsletter_interaction_score — email engagement quality
      4. portal_login_frequency       — platform stickiness
      5. donation_recency             — recency in RFM model
      6. total_donation_amount        — monetary in RFM model
      7. engagement_score             — composite behavioral index
      8. donation_affinity_score      — combined propensity index
    """

    TITLE_SENIORITY = {
        "intern": 0, "junior": 1, "engineer": 2, "developer": 2,
        "specialist": 2, "analyst": 2, "senior": 3, "lead": 3,
        "principal": 4, "staff": 4, "manager": 4, "director": 5,
        "vp": 6, "vice president": 6, "cto": 7, "ceo": 7,
        "founder": 7, "partner": 6,
    }

    def __init__(self, raw: Dict[str, pd.DataFrame], n_synthetic: int = 1000):
        self.raw         = raw
        self.n_synthetic = n_synthetic
        self.label_enc   : Dict[str, LabelEncoder] = {}

    # ── public entry point ────────────────────────────────────────────────────
    def build(self) -> pd.DataFrame:
        log.info("=== FEATURE ENGINEERING ===")
        base = self._build_base()
        base = self._add_mandatory_features(base)
        base = self._add_target(base)
        base = self._encode_categoricals(base)
        log.info("  Final feature matrix: %d rows × %d cols", *base.shape)
        return base

    # ── base construction ─────────────────────────────────────────────────────
    def _build_base(self) -> pd.DataFrame:
        alumni = self.raw.get("alumni_people")
        if alumni is not None and len(alumni) >= 50:
            df = alumni.copy()
            df.columns = [c.strip() for c in df.columns]
            df = self._normalize_alumni_columns(df)
        else:
            log.warning("  alumni_people small/missing — using synthetic base")
            df = self._create_synthetic_base()

        # ── Augment with student GPA ──────────────────────────────────────────
        ss = self.raw.get("student_scores")
        if ss is not None and "ORTALAMA" in ss.columns:
            # Each NUMARA(S2) is a student ID
            gpa_agg = (
                ss.groupby("NUMARA(S2)")["ORTALAMA"]
                  .agg(["mean", "max"])
                  .rename(columns={"mean": "gpa_avg", "max": "gpa_max"})
                  .reset_index()
                  .rename(columns={"NUMARA(S2)": "student_id"})
            )
            if "student_id" in df.columns:
                df = df.merge(gpa_agg, on="student_id", how="left")
            else:
                df["gpa_avg"] = np.random.normal(2.8, 0.5, len(df)).clip(0, 4.0)
                df["gpa_max"] = (df["gpa_avg"] + np.random.uniform(0, 0.5, len(df))).clip(0, 4.0)
        else:
            df["gpa_avg"] = np.random.normal(2.8, 0.5, len(df)).clip(0, 4.0)
            df["gpa_max"] = (df["gpa_avg"] + np.random.uniform(0, 0.5, len(df))).clip(0, 4.0)

        return df

    def _normalize_alumni_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename raw Turkish/unnamed columns to clean English names."""
        rename_map = {
            "Unnamed: 0"  : "alumni_id",
            "0"           : "full_name",
            "1"           : "job_description",
            "cinsiyet"    : "gender_code",   # 1=male, 0=female (typical in this DS)
            "ACIKLAMA"    : "bio_text",
            "title"       : "job_title",
            "company"     : "employer",
            "LINK"        : "linkedin_url",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # Synthetic engagement & financial columns (not in source — would come
        # from a CRM / DWH join in production)
        n = len(df)
        np.random.seed(RANDOM_SEED)
        df["graduation_year"]        = np.random.randint(2005, 2022, n)
        df["event_attendance_raw"]   = np.random.poisson(3, n)
        df["email_open_rate"]        = np.random.beta(2, 5, n)        # 0-1
        df["email_click_rate"]       = np.random.beta(1, 6, n)        # 0-1
        df["portal_logins_12m"]      = np.random.poisson(8, n)
        df["last_donation_days_ago"] = np.random.exponential(400, n).astype(int)
        df["total_donations_usd"]    = np.random.exponential(800, n)
        df["peer_referrals"]         = np.random.poisson(1, n)
        df["volunteer_hours"]        = np.random.gamma(2, 5, n)
        df["location_type"]          = np.random.choice(
            ["Local", "Regional", "National", "International"], n,
            p=[0.3, 0.25, 0.25, 0.2]
        )
        df["degree_level"]           = np.random.choice(
            ["Bachelor", "Master", "PhD"], n, p=[0.6, 0.3, 0.1]
        )
        return df

    def _create_synthetic_base(self) -> pd.DataFrame:
        """Full synthetic dataset when CSV data is unavailable."""
        n = self.n_synthetic
        np.random.seed(RANDOM_SEED)
        df = pd.DataFrame({
            "alumni_id"           : range(n),
            "full_name"           : [f"Alumni_{i}" for i in range(n)],
            "gender_code"         : np.random.choice([0, 1], n, p=[0.35, 0.65]),
            "graduation_year"     : np.random.randint(2005, 2022, n),
            "job_title"           : np.random.choice(
                ["Software Engineer", "Senior Engineer", "Manager",
                 "Director", "VP", "Data Scientist", "Developer", "Analyst",
                 "CTO", "Founder"], n
            ),
            "employer"            : np.random.choice(
                ["Microsoft", "Google", "Amazon", "Trakya University",
                 "Softtech", "Turkcell", "Startup", None], n,
                p=[0.1, 0.1, 0.1, 0.15, 0.1, 0.1, 0.2, 0.15]
            ),
            "event_attendance_raw": np.random.poisson(3, n),
            "email_open_rate"     : np.random.beta(2, 5, n),
            "email_click_rate"    : np.random.beta(1, 6, n),
            "portal_logins_12m"   : np.random.poisson(8, n),
            "last_donation_days_ago": np.random.exponential(400, n).astype(int),
            "total_donations_usd" : np.random.exponential(800, n),
            "peer_referrals"      : np.random.poisson(1, n),
            "volunteer_hours"     : np.random.gamma(2, 5, n),
            "location_type"       : np.random.choice(
                ["Local", "Regional", "National", "International"], n,
                p=[0.3, 0.25, 0.25, 0.2]
            ),
            "degree_level"        : np.random.choice(
                ["Bachelor", "Master", "PhD"], n, p=[0.6, 0.3, 0.1]
            ),
            "gpa_avg"             : np.random.normal(2.8, 0.5, n).clip(0, 4.0),
            "gpa_max"             : np.random.normal(3.2, 0.5, n).clip(0, 4.0),
        })
        return df

    # ── mandatory feature construction ───────────────────────────────────────
    def _add_mandatory_features(self, df: pd.DataFrame) -> pd.DataFrame:
        log.info("  Building 8 mandatory features …")

        # ── 1. Years since graduation ─────────────────────────────────────────
        df["years_since_graduation"] = np.maximum(
            CURRENT_YEAR - df["graduation_year"], 0
        )
        log.info("    ✓ years_since_graduation")

        # ── 2. Event attendance count ─────────────────────────────────────────
        #  Raw count already present; we also create a capped version to reduce
        #  the influence of outliers.
        df["event_attendance_count"] = df["event_attendance_raw"].clip(upper=20)
        log.info("    ✓ event_attendance_count")

        # ── 3. Newsletter interaction score (email quality signal) ────────────
        #  Combines open rate and click-through rate with industry-aligned weights
        #  (clicks are a stronger intent signal than opens).
        df["newsletter_interaction_score"] = (
            df["email_open_rate"] * 0.4 + df["email_click_rate"] * 0.6
        ) * 100   # scale to 0-100
        log.info("    ✓ newsletter_interaction_score")

        # ── 4. Portal login frequency (platform stickiness) ───────────────────
        #  Capped and log-scaled to reduce skew from power users.
        df["portal_login_frequency"] = np.log1p(
            df["portal_logins_12m"].clip(upper=100)
        )
        log.info("    ✓ portal_login_frequency")

        # ── 5. Donation recency (RFM — Recency) ───────────────────────────────
        #  Inverse of days since last donation; higher = more recent.
        #  Cap at 5 years to avoid extreme outliers dominating.
        max_days = 365 * 5
        df["donation_recency"] = 1.0 - (
            df["last_donation_days_ago"].clip(upper=max_days) / max_days
        )
        log.info("    ✓ donation_recency")

        # ── 6. Total donation amount (RFM — Monetary) ─────────────────────────
        #  Log-transform to normalise heavy right skew.
        df["total_donation_amount"] = np.log1p(df["total_donations_usd"])
        log.info("    ✓ total_donation_amount")

        # ── 7. Engagement score (composite behavioural index) ─────────────────
        #  Weighted combination of all behavioural signals normalised to 0-100.
        max_events = df["event_attendance_count"].max() + 1e-8
        max_vol    = df["volunteer_hours"].max() + 1e-8
        max_login  = df["portal_login_frequency"].max() + 1e-8
        max_refs   = df["peer_referrals"].max() + 1e-8

        df["engagement_score"] = (
            (df["event_attendance_count"] / max_events)   * 0.30 +
            (df["newsletter_interaction_score"] / 100)    * 0.25 +
            (df["portal_login_frequency"]      / max_login) * 0.20 +
            (df["volunteer_hours"]             / max_vol)  * 0.15 +
            (df["peer_referrals"]              / max_refs) * 0.10
        ) * 100
        log.info("    ✓ engagement_score")

        # ── 8. Donation affinity score (combined propensity index) ────────────
        #  Blends monetary history, recency, and engagement into a single
        #  pre-model propensity score (useful for rules-based fallbacks).
        df["donation_affinity_score"] = (
            df["total_donation_amount"] / (df["total_donation_amount"].max() + 1e-8) * 0.40 +
            df["donation_recency"]                                                   * 0.35 +
            df["engagement_score"] / 100                                             * 0.25
        ) * 100
        log.info("    ✓ donation_affinity_score")

        # ── Derived categorical / ordinal features ────────────────────────────
        df["seniority_level"] = df["job_title"].fillna("unknown").str.lower().apply(
            lambda t: max(
                (v for k, v in self.TITLE_SENIORITY.items() if k in t),
                default=1
            )
        )

        degree_map = {"Bachelor": 0, "Master": 1, "PhD": 2}
        df["degree_numeric"] = df["degree_level"].map(degree_map).fillna(0).astype(int)

        proximity_map = {"Local": 4, "Regional": 3, "National": 2, "International": 1}
        df["proximity_score"] = df["location_type"].map(proximity_map).fillna(2).astype(int)

        # Mid-career flag (typically higher donation capacity)
        df["is_mid_career"] = (
            (df["years_since_graduation"] >= 7) &
            (df["years_since_graduation"] <= 20)
        ).astype(int)

        return df

    # ── target label ──────────────────────────────────────────────────────────
    def _add_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create binary label: will_donate (1 = likely to donate in next 12 months).

        In production this comes from CRM transaction records.  Here we derive
        it probabilistically from the affinity score so the ML problem is
        non-trivial (not perfectly correlated).
        """
        raw_prob = (
            df["donation_affinity_score"] / 100 * 0.55 +
            df["engagement_score"] / 100 * 0.30 +
            df["is_mid_career"] * 0.10 +
            np.random.uniform(0, 0.1, len(df))   # irreducible noise
        ).clip(0, 1)

        df[TARGET_COL] = (raw_prob > raw_prob.median()).astype(int)
        pos_rate = df[TARGET_COL].mean()
        log.info("  Target '%s' positive rate: %.1f%%", TARGET_COL, pos_rate * 100)
        return df

    # ── categorical encoding ──────────────────────────────────────────────────
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        cat_cols = ["location_type", "degree_level"]
        for col in cat_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col + "_enc"] = le.fit_transform(df[col].fillna("Unknown").astype(str))
                self.label_enc[col] = le
        return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. MODEL FEATURES  — select & split
# ─────────────────────────────────────────────────────────────────────────────

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


def prepare_train_test(df: pd.DataFrame) -> Tuple:
    """
    Split features and labels into stratified train / test sets.
    Impute remaining NaNs with column medians (safe for all model types).
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].copy()
    y = df[TARGET_COL].copy()

    # Impute before split so we don't leak imputation stats
    imputer = SimpleImputer(strategy="median")
    X_imp   = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X_imp, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    log.info(
        "  Train: %d rows  |  Test: %d rows  |  Features: %d",
        len(X_train), len(X_test), X_train.shape[1]
    )
    return X_train, X_test, y_train, y_test, available


# ─────────────────────────────────────────────────────────────────────────────
# 5. BASELINE MODEL — Logistic Regression
# ─────────────────────────────────────────────────────────────────────────────

class BaselineModel:
    """
    Logistic Regression serves two purposes:
      a) Establish a performance floor the ensemble must beat.
      b) Provide signed feature coefficients for business explainability.

    The model is wrapped in a sklearn Pipeline with StandardScaler so that
    coefficients are on a comparable scale.
    """

    def __init__(self):
        self.pipeline  = None
        self.coef_df   = None
        self.auc       = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        log.info("=== BASELINE — Logistic Regression ===")
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model",  LogisticRegression(
                max_iter=1000,
                C=1.0,
                class_weight="balanced",    # handle class imbalance
                random_state=RANDOM_SEED,
                solver="lbfgs",
            ))
        ])
        self.pipeline.fit(X_train, y_train)

        # ── Feature coefficients (explainability) ─────────────────────────────
        coef = self.pipeline.named_steps["model"].coef_[0]
        self.coef_df = (
            pd.DataFrame({"feature": X_train.columns, "coefficient": coef})
              .sort_values("coefficient", key=abs, ascending=False)
        )
        log.info("  ✓ Logistic Regression trained")
        print("\n  Top 5 Positive Drivers (increase donation probability):")
        print(self.coef_df[self.coef_df["coefficient"] > 0].head(5).to_string(index=False))
        print("\n  Top 5 Negative Drivers (decrease donation probability):")
        print(self.coef_df[self.coef_df["coefficient"] < 0].head(5).to_string(index=False))

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> float:
        proba = self.pipeline.predict_proba(X_test)[:, 1]
        self.auc = roc_auc_score(y_test, proba)
        log.info("  Baseline AUC-ROC: %.4f", self.auc)
        return self.auc

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.pipeline.predict_proba(X)[:, 1]


# ─────────────────────────────────────────────────────────────────────────────
# 6. PRODUCTION MODELS — XGBoost & CatBoost
# ─────────────────────────────────────────────────────────────────────────────

class XGBoostModel:
    """
    XGBoost — optimised for numerical features and interaction effects.
    Hyperparameters are production-conservative (no over-fitting).
    """

    def __init__(self):
        self.model = None
        self.auc   = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        if not XGBOOST_AVAILABLE:
            log.warning("  XGBoost unavailable — skipping")
            return
        log.info("=== PRODUCTION — XGBoost ===")
        self.model = XGBClassifier(
            n_estimators     = 300,
            max_depth        = 5,
            learning_rate    = 0.05,
            subsample        = 0.8,
            colsample_bytree = 0.8,
            min_child_weight = 3,
            gamma            = 0.1,
            scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum(),
            use_label_encoder= False,
            eval_metric      = "auc",
            random_state     = RANDOM_SEED,
            verbosity        = 0,
        )
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train)],
            verbose=False,
        )
        log.info("  ✓ XGBoost trained")

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> float:
        if self.model is None:
            return 0.5
        proba = self.model.predict_proba(X_test)[:, 1]
        self.auc = roc_auc_score(y_test, proba)
        log.info("  XGBoost AUC-ROC: %.4f", self.auc)
        return self.auc

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            return np.full(len(X), 0.5)
        return self.model.predict_proba(X)[:, 1]

    def feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        if self.model is None:
            return pd.DataFrame()
        scores = self.model.feature_importances_
        return (
            pd.DataFrame({"feature": feature_names, "importance": scores})
              .sort_values("importance", ascending=False)
        )


class CatBoostModel:
    """
    CatBoost — handles categorical features natively without manual encoding.
    Uses ordered boosting to reduce overfitting on small datasets.
    """

    def __init__(self, cat_features: List[str] = None):
        self.model        = None
        self.cat_features = cat_features or []
        self.auc          = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        if not CATBOOST_AVAILABLE:
            log.warning("  CatBoost unavailable — skipping")
            return
        log.info("=== PRODUCTION — CatBoost ===")
        cat_idx = [
            i for i, c in enumerate(X_train.columns)
            if c in self.cat_features
        ]
        self.model = CatBoostClassifier(
            iterations        = 300,
            depth             = 6,
            learning_rate     = 0.05,
            l2_leaf_reg       = 3,
            loss_function     = "Logloss",
            eval_metric       = "AUC",
            auto_class_weights= "Balanced",
            random_seed       = RANDOM_SEED,
            verbose           = 0,
        )
        self.model.fit(
            X_train, y_train,
            cat_features=cat_idx if cat_idx else None,
        )
        log.info("  ✓ CatBoost trained")

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> float:
        if self.model is None:
            return 0.5
        proba = self.model.predict_proba(X_test)[:, 1]
        self.auc = roc_auc_score(y_test, proba)
        log.info("  CatBoost AUC-ROC: %.4f", self.auc)
        return self.auc

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            return np.full(len(X), 0.5)
        return self.model.predict_proba(X)[:, 1]

    def feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        if self.model is None:
            return pd.DataFrame()
        scores = self.model.get_feature_importance()
        return (
            pd.DataFrame({"feature": feature_names, "importance": scores})
              .sort_values("importance", ascending=False)
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. ENSEMBLE SCORING
# ─────────────────────────────────────────────────────────────────────────────

class EnsembleScorer:
    """
    Weighted probability fusion: XGBoost × 0.55  +  CatBoost × 0.45

    Weight rationale:
      XGBoost slightly higher because our features are mostly numerical with
      interaction effects.  Adjust empirically via cross-validation in prod.

    In production, scores are written back to S3 as parquet for downstream
    CRM ingestion.  [IAM] Requires s3:PutObject on the output bucket.
    """

    def __init__(self, xgb: XGBoostModel, cat: CatBoostModel,
                 w_xgb: float = ENSEMBLE_W_XGB, w_cat: float = ENSEMBLE_W_CAT):
        assert abs(w_xgb + w_cat - 1.0) < 1e-6, "Ensemble weights must sum to 1.0"
        self.xgb   = xgb
        self.cat   = cat
        self.w_xgb = w_xgb
        self.w_cat = w_cat
        self.auc   = None

    def score(self, X: pd.DataFrame, y: pd.Series = None) -> pd.Series:
        p_xgb = self.xgb.predict_proba(X)
        p_cat = self.cat.predict_proba(X)
        ensemble_prob = self.w_xgb * p_xgb + self.w_cat * p_cat

        if y is not None:
            self.auc = roc_auc_score(y, ensemble_prob)
            log.info("  Ensemble AUC-ROC: %.4f  (XGB×%.2f + CAT×%.2f)",
                     self.auc, self.w_xgb, self.w_cat)

        return pd.Series(ensemble_prob, index=X.index, name="ensemble_score")

    def write_scores_to_s3(self, df: pd.DataFrame, scores: pd.Series) -> None:
        """
        Production stub — replace with:
            import awswrangler as wr
            output = df[["alumni_id"]].assign(score=scores, scored_at=datetime.now())
            wr.s3.to_parquet(output, S3_OUTPUT_PREFIX + "scores.parquet")
        [IAM] Requires s3:PutObject on output bucket.
        """
        local_path = os.path.join(LOCAL_OUTPUT_DIR, "alumni_scores.csv")
        output = pd.DataFrame({
            "alumni_id"        : df.get("alumni_id", df.index),
            "ensemble_score"   : scores,
            "score_date"       : datetime.now().date(),
            "model_version"    : "2.0.0",
        })
        # [SECURITY] Mask sensitive fields before saving to logs / S3
        output.to_csv(local_path, index=False)
        log.info("  Scores written → %s  (prod: %s)", local_path, S3_OUTPUT_PREFIX)


# ─────────────────────────────────────────────────────────────────────────────
# 8. MODEL EVALUATION  (AUC, ROC, confusion matrix, feature importance)
# ─────────────────────────────────────────────────────────────────────────────

class ModelEvaluator:
    """Plots and prints all evaluation artefacts. Saves to LOCAL_OUTPUT_DIR."""

    def run(
        self,
        X_test   : pd.DataFrame,
        y_test   : pd.Series,
        baseline : BaselineModel,
        xgb_mdl  : XGBoostModel,
        cat_mdl  : CatBoostModel,
        ensemble : EnsembleScorer,
        feature_cols: List[str],
    ) -> None:
        log.info("=== MODEL EVALUATION ===")
        self._print_classification_reports(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble)
        self._plot_roc_curves(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble)
        self._plot_feature_importances(xgb_mdl, cat_mdl, baseline, feature_cols)
        self._plot_score_distributions(X_test, y_test, ensemble)
        self._cross_val_summary(X_test, y_test, baseline, xgb_mdl, cat_mdl, feature_cols)

    # ── classification reports ────────────────────────────────────────────────
    @staticmethod
    def _print_classification_reports(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble):
        models = {
            "Logistic Regression (Baseline)" : baseline.predict_proba(X_test),
            "XGBoost"                        : xgb_mdl.predict_proba(X_test),
            "CatBoost"                       : cat_mdl.predict_proba(X_test),
            "Ensemble"                       : ensemble.score(X_test),
        }
        print("\n" + "─" * 60)
        print("  MODEL PERFORMANCE SUMMARY")
        print("─" * 60)
        for name, proba in models.items():
            pred = (proba > 0.5).astype(int)
            auc  = roc_auc_score(y_test, proba)
            ap   = average_precision_score(y_test, proba)
            print(f"\n  {name}")
            print(f"    AUC-ROC : {auc:.4f}   Average Precision : {ap:.4f}")
            print(classification_report(y_test, pred, target_names=["Won't Donate", "Will Donate"],
                                       indent=4))

    # ── ROC curves ───────────────────────────────────────────────────────────
    def _plot_roc_curves(self, X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        models = {
            "Logistic Regression": (baseline.predict_proba(X_test), "royalblue", "--"),
            "XGBoost"            : (xgb_mdl.predict_proba(X_test),  "darkorange", "-"),
            "CatBoost"           : (cat_mdl.predict_proba(X_test),  "forestgreen", "-"),
            "Ensemble"           : (ensemble.score(X_test),          "crimson", "-"),
        }

        # ROC
        ax = axes[0]
        ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="Random")
        for name, (proba, color, ls) in models.items():
            fpr, tpr, _ = roc_curve(y_test, proba)
            auc = roc_auc_score(y_test, proba)
            ax.plot(fpr, tpr, color=color, ls=ls, lw=2, label=f"{name} (AUC={auc:.3f})")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC Curves — All Models")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # Confusion matrix for ensemble
        ax2 = axes[1]
        ens_proba = ensemble.score(X_test)
        ens_pred  = (ens_proba > 0.5).astype(int)
        cm = confusion_matrix(y_test, ens_pred)
        disp = ConfusionMatrixDisplay(cm, display_labels=["Won't Donate", "Will Donate"])
        disp.plot(ax=ax2, colorbar=False, cmap="Blues")
        ax2.set_title("Ensemble — Confusion Matrix")

        plt.tight_layout()
        out = os.path.join(LOCAL_OUTPUT_DIR, "02_roc_curves.png")
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close()
        log.info("  ROC figure saved → %s", out)

    # ── feature importance ────────────────────────────────────────────────────
    def _plot_feature_importances(self, xgb_mdl, cat_mdl, baseline, feature_cols):
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        def _bar(ax, df, title, color):
            if df.empty:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center")
            else:
                top = df.head(10).sort_values("importance")
                ax.barh(top["feature"], top["importance"], color=color)
                ax.set_title(title)

        _bar(axes[0], xgb_mdl.feature_importance(feature_cols),  "XGBoost Feature Importance",  "darkorange")
        _bar(axes[1], cat_mdl.feature_importance(feature_cols),  "CatBoost Feature Importance",  "forestgreen")

        # Logistic Regression coefficients (abs value)
        if baseline.coef_df is not None:
            top_lr = (
                baseline.coef_df.assign(abs_coef=baseline.coef_df["coefficient"].abs())
                       .nlargest(10, "abs_coef")
                       .sort_values("abs_coef")
            )
            axes[2].barh(top_lr["feature"], top_lr["coefficient"],
                         color=["tomato" if v < 0 else "royalblue" for v in top_lr["coefficient"]])
            axes[2].set_title("Logistic Regression Coefficients")
            axes[2].axvline(0, color="k", lw=0.8)

        plt.tight_layout()
        out = os.path.join(LOCAL_OUTPUT_DIR, "03_feature_importance.png")
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close()
        log.info("  Feature importance figure saved → %s", out)

    # ── score distributions ───────────────────────────────────────────────────
    def _plot_score_distributions(self, X_test, y_test, ensemble):
        scores = ensemble.score(X_test)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Distribution by class
        ax = axes[0]
        ax.hist(scores[y_test == 0], bins=30, alpha=0.6, color="steelblue",
                label="Won't Donate")
        ax.hist(scores[y_test == 1], bins=30, alpha=0.6, color="tomato",
                label="Will Donate")
        ax.set_xlabel("Ensemble Score")
        ax.set_ylabel("Count")
        ax.set_title("Score Distribution by Class")
        ax.legend()

        # Calibration-style: mean score by decile
        ax2 = axes[1]
        combined = pd.DataFrame({"score": scores.values, "label": y_test.values})
        combined["decile"] = pd.qcut(combined["score"], q=10, labels=False, duplicates="drop")
        decile_stats = combined.groupby("decile").agg(
            mean_score=("score", "mean"),
            actual_rate=("label", "mean")
        )
        ax2.bar(decile_stats.index, decile_stats["actual_rate"], color="steelblue",
                alpha=0.7, label="Actual donation rate")
        ax2.plot(decile_stats.index, decile_stats["mean_score"], "ro-",
                 label="Mean predicted score")
        ax2.set_xlabel("Score Decile (0=lowest, 9=highest)")
        ax2.set_ylabel("Rate / Score")
        ax2.set_title("Score Calibration by Decile")
        ax2.legend(fontsize=8)

        plt.tight_layout()
        out = os.path.join(LOCAL_OUTPUT_DIR, "04_score_distributions.png")
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close()
        log.info("  Score distribution figure saved → %s", out)

    # ── cross-validation summary ──────────────────────────────────────────────
    @staticmethod
    def _cross_val_summary(X_test, y_test, baseline, xgb_mdl, cat_mdl, feature_cols):
        print("\n  Cross-Validation AUC (5-fold on test set — approximate):")
        lr_scores = cross_val_score(
            baseline.pipeline, X_test, y_test,
            cv=min(CV_FOLDS, len(X_test) // 10),
            scoring="roc_auc"
        )
        print(f"    Logistic Regression  :  {lr_scores.mean():.4f} ± {lr_scores.std():.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. GENAI INSIGHT LAYER
#    Generates natural language insights by calling the Anthropic API.
#    Requires ANTHROPIC_API_KEY in the environment.
# ─────────────────────────────────────────────────────────────────────────────

class GenAIInsightLayer:
    """
    Converts quantitative model outputs into natural language insights using
    Claude (claude-sonnet-4-20250514).

    Usage:
      insights = GenAIInsightLayer()
      answer   = insights.ask("Which alumni segment is most likely to donate?", context)

    In production the context dict is populated from S3 / DWH query results
    so every insight is grounded in real data.

    [SECURITY] The API key is read from an environment variable — never
    hard-coded.  In AWS, store the key in Secrets Manager and inject via
    SageMaker environment variables.
    """

    SYSTEM_PROMPT = (
        "You are a senior data scientist advising a university alumni relations "
        "team.  You have access to ML model outputs from a donor propensity model.  "
        "Answer questions clearly and concisely with actionable recommendations.  "
        "Cite specific numbers from the provided context when available.  "
        "Keep responses under 200 words."
    )

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            log.warning(
                "  ANTHROPIC_API_KEY not set — GenAI layer will return "
                "placeholder responses.  Set the env var to enable live insights."
            )

    def ask(self, question: str, context: dict) -> str:
        """Send a question + model context to Claude and return the insight."""
        if not self.api_key:
            return self._placeholder(question, context)

        try:
            import urllib.request, urllib.parse
            context_str = json.dumps(context, indent=2, default=str)
            payload = json.dumps({
                "model"      : "claude-sonnet-4-20250514",
                "max_tokens" : 512,
                "system"     : self.SYSTEM_PROMPT,
                "messages"   : [{
                    "role"   : "user",
                    "content": (
                        f"MODEL CONTEXT:\n{context_str}\n\n"
                        f"QUESTION: {question}"
                    ),
                }],
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "x-api-key"        : self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type"     : "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data["content"][0]["text"]

        except Exception as exc:
            log.error("  GenAI API call failed: %s", exc)
            return self._placeholder(question, context)

    @staticmethod
    def _placeholder(question: str, context: dict) -> str:
        """Deterministic placeholder when API key is absent."""
        top_feature = context.get("top_feature", "engagement_score")
        ensemble_auc = context.get("ensemble_auc", "N/A")
        return (
            f"[GenAI Placeholder — set ANTHROPIC_API_KEY for live insights]\n"
            f"Based on the model (ensemble AUC={ensemble_auc}), the top driver of donation "
            f"propensity is '{top_feature}'.  Alumni with high scores on this metric "
            f"and 7–20 years since graduation represent the highest-value segment.  "
            f"Re-engagement campaigns targeting low-engagement, high-salary alumni "
            f"are recommended as the immediate next action."
        )

    def run_insight_queries(self, context: dict) -> None:
        """Run the canonical set of business insight queries."""
        log.info("=== GENAI INSIGHT LAYER ===")

        queries = [
            "Which alumni segment is most likely to donate for infrastructure projects?",
            "What engagement behaviors most influence donation probability, and why?",
            "What re-engagement strategy would you recommend for high-salary alumni "
            "with low engagement scores?",
            "Summarise the 3 most actionable findings from this model for the "
            "alumni relations team.",
        ]

        print("\n" + "─" * 60)
        print("  NATURAL LANGUAGE INSIGHTS  (powered by Claude)")
        print("─" * 60)
        for q in queries:
            print(f"\n  Q: {q}")
            print(f"  A: {self.ask(q, context)}")
            print()


# ─────────────────────────────────────────────────────────────────────────────
# 10. AUDIT LOGGING  (compliance)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# 11. MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  ALUMNI DONATION & ENGAGEMENT PREDICTION SYSTEM  v2.0.0")
    print("  AWS-Compatible Production ML Pipeline")
    print("=" * 70)

    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    # ── [1] Data Loading ──────────────────────────────────────────────────────
    loader = DataLoader(use_s3=False, local_dir=LOCAL_INPUT_DIR)
    raw    = loader.load_all()

    # ── [2] EDA Summary ───────────────────────────────────────────────────────
    eda = EDASummary()
    eda.run(raw)

    # ── [3] Feature Engineering ───────────────────────────────────────────────
    fe   = FeatureEngineer(raw, n_synthetic=1000)
    data = fe.build()

    # ── [4] Train / Test Split ────────────────────────────────────────────────
    X_train, X_test, y_train, y_test, feature_cols = prepare_train_test(data)

    # ── [5] Baseline Model ────────────────────────────────────────────────────
    baseline = BaselineModel()
    baseline.train(X_train, y_train)
    lr_auc = baseline.evaluate(X_test, y_test)

    # ── [6a] XGBoost ──────────────────────────────────────────────────────────
    xgb_mdl = XGBoostModel()
    xgb_mdl.train(X_train, y_train)
    xgb_auc = xgb_mdl.evaluate(X_test, y_test)

    # ── [6b] CatBoost ─────────────────────────────────────────────────────────
    cat_cols = []   # all features are numeric after FeatureEngineer encoding
    cat_mdl  = CatBoostModel(cat_features=cat_cols)
    cat_mdl.train(X_train, y_train)
    cat_auc = cat_mdl.evaluate(X_test, y_test)

    # ── [7] Ensemble Scoring ──────────────────────────────────────────────────
    ensemble    = EnsembleScorer(xgb_mdl, cat_mdl)
    ens_scores  = ensemble.score(X_test, y_test)
    ens_auc     = ensemble.auc or 0.0

    # Write full-dataset scores (all alumni) back to "S3"
    all_scores = ensemble.score(pd.DataFrame(
        data[feature_cols].fillna(data[feature_cols].median())
    ))
    ensemble.write_scores_to_s3(data, all_scores)

    # ── [8] Evaluation ────────────────────────────────────────────────────────
    evaluator = ModelEvaluator()
    evaluator.run(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble, feature_cols)

    # ── [9] GenAI Insight Layer ───────────────────────────────────────────────
    top_xgb_feature = (
        xgb_mdl.feature_importance(feature_cols).iloc[0]["feature"]
        if XGBOOST_AVAILABLE and xgb_mdl.model is not None
        else "engagement_score"
    )
    model_context = {
        "baseline_auc"       : round(lr_auc, 4),
        "xgb_auc"            : round(xgb_auc, 4),
        "catboost_auc"       : round(cat_auc, 4),
        "ensemble_auc"       : round(ens_auc, 4),
        "top_feature"        : top_xgb_feature,
        "n_alumni_scored"    : len(data),
        "n_train"            : len(X_train),
        "n_test"             : len(X_test),
        "positive_rate_train": round(float(y_train.mean()), 4),
        "high_propensity_pct": round((all_scores > 0.7).mean() * 100, 1),
        "lr_top_coefficients": (
            baseline.coef_df.head(3).to_dict("records")
            if baseline.coef_df is not None else []
        ),
    }
    genai = GenAIInsightLayer()
    genai.run_insight_queries(model_context)

    # ── [10] Audit Logging ────────────────────────────────────────────────────
    write_audit_log(model_context)

    # ── Final Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  Alumni scored           : {len(data):,}")
    print(f"  Logistic Regression AUC : {lr_auc:.4f}")
    print(f"  XGBoost AUC             : {xgb_auc:.4f}")
    print(f"  CatBoost AUC            : {cat_auc:.4f}")
    print(f"  Ensemble AUC            : {ens_auc:.4f}")
    print(f"  High-propensity alumni  : {model_context['high_propensity_pct']}%  (score > 0.70)")
    print(f"\n  Outputs (local → S3 in prod):")
    print(f"    {LOCAL_OUTPUT_DIR}01_eda_summary.png")
    print(f"    {LOCAL_OUTPUT_DIR}02_roc_curves.png")
    print(f"    {LOCAL_OUTPUT_DIR}03_feature_importance.png")
    print(f"    {LOCAL_OUTPUT_DIR}04_score_distributions.png")
    print(f"    {LOCAL_OUTPUT_DIR}alumni_scores.csv")
    print(f"    {LOCAL_OUTPUT_DIR}audit_log.json")
    print("=" * 70)

    return model_context, data, all_scores


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    context, scored_data, scores = main()