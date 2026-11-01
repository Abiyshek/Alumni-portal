"""
Feature Engineering Module
Builds the model-ready feature matrix from raw datasets.
"""

import logging
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from .config import CURRENT_YEAR, RANDOM_SEED, TEST_SIZE, TARGET_COL, FEATURE_COLS

log = logging.getLogger("alumni_pipeline")


class FeatureEngineer:
    """
    Builds the model-ready feature matrix from raw datasets.

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
            "cinsiyet"    : "gender_code",
            "ACIKLAMA"    : "bio_text",
            "title"       : "job_title",
            "company"     : "employer",
            "LINK"        : "linkedin_url",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # Synthetic engagement & financial columns
        n = len(df)
        np.random.seed(RANDOM_SEED)
        df["graduation_year"]        = np.random.randint(2005, 2022, n)
        df["event_attendance_raw"]   = np.random.poisson(3, n)
        df["email_open_rate"]        = np.random.beta(2, 5, n)
        df["email_click_rate"]       = np.random.beta(1, 6, n)
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

        df["years_since_graduation"] = np.maximum(CURRENT_YEAR - df["graduation_year"], 0)
        log.info("    ✓ years_since_graduation")

        df["event_attendance_count"] = df["event_attendance_raw"].clip(upper=20)
        log.info("    ✓ event_attendance_count")

        df["newsletter_interaction_score"] = (
            df["email_open_rate"] * 0.4 + df["email_click_rate"] * 0.6
        ) * 100
        log.info("    ✓ newsletter_interaction_score")

        df["portal_login_frequency"] = np.log1p(df["portal_logins_12m"].clip(upper=100))
        log.info("    ✓ portal_login_frequency")

        max_days = 365 * 5
        df["donation_recency"] = 1.0 - (
            df["last_donation_days_ago"].clip(upper=max_days) / max_days
        )
        log.info("    ✓ donation_recency")

        df["total_donation_amount"] = np.log1p(df["total_donations_usd"])
        log.info("    ✓ total_donation_amount")

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

        df["donation_affinity_score"] = (
            df["total_donation_amount"] / (df["total_donation_amount"].max() + 1e-8) * 0.40 +
            df["donation_recency"]                                                   * 0.35 +
            df["engagement_score"] / 100                                             * 0.25
        ) * 100
        log.info("    ✓ donation_affinity_score")

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

        df["is_mid_career"] = (
            (df["years_since_graduation"] >= 7) &
            (df["years_since_graduation"] <= 20)
        ).astype(int)

        return df

    # ── target label ──────────────────────────────────────────────────────────
    def _add_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create binary label: will_donate."""
        raw_prob = (
            df["donation_affinity_score"] / 100 * 0.55 +
            df["engagement_score"] / 100 * 0.30 +
            df["is_mid_career"] * 0.10 +
            np.random.uniform(0, 0.1, len(df))
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


def prepare_train_test(df: pd.DataFrame) -> Tuple:
    """
    Split features and labels into stratified train / test sets.
    Impute remaining NaNs with column medians.
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].copy()
    y = df[TARGET_COL].copy()

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
