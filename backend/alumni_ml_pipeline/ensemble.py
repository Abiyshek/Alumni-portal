"""
Ensemble Scoring Module
Weighted probability fusion for XGBoost and CatBoost models.
"""

import os
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .config import LOCAL_OUTPUT_DIR, ENSEMBLE_W_XGB, ENSEMBLE_W_CAT, S3_OUTPUT_PREFIX

log = logging.getLogger("alumni_pipeline")


class EnsembleScorer:
    """
    Weighted probability fusion: XGBoost × 0.55  +  CatBoost × 0.45

    Weight rationale:
      XGBoost slightly higher because features are mostly numerical with
      interaction effects.  Adjust empirically via cross-validation in prod.
    """

    def __init__(self, xgb, cat, w_xgb: float = ENSEMBLE_W_XGB, w_cat: float = ENSEMBLE_W_CAT):
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
        """
        local_path = os.path.join(LOCAL_OUTPUT_DIR, "alumni_scores.csv")
        output = pd.DataFrame({
            "alumni_id"        : df.get("alumni_id", df.index),
            "ensemble_score"   : scores,
            "score_date"       : datetime.now().date(),
            "model_version"    : "2.0.0",
        })
        output.to_csv(local_path, index=False)
        log.info("  Scores written → %s  (prod: %s)", local_path, S3_OUTPUT_PREFIX)
