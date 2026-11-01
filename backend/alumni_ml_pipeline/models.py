"""
Machine Learning Models Module
Contains Baseline, XGBoost, and CatBoost models.
"""

import logging
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

from .config import RANDOM_SEED

log = logging.getLogger("alumni_pipeline")

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    log.warning("[WARN] xgboost not installed — XGBoost layer will be skipped.")

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    log.warning("[WARN] catboost not installed — CatBoost layer will be skipped.")


class BaselineModel:
    """
    Logistic Regression serves two purposes:
      a) Establish a performance floor the ensemble must beat.
      b) Provide signed feature coefficients for business explainability.
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
                class_weight="balanced",
                random_state=RANDOM_SEED,
                solver="lbfgs",
            ))
        ])
        self.pipeline.fit(X_train, y_train)

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

    def __init__(self, cat_features: Optional[List[str]] = None):
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
