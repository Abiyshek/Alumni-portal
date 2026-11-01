"""
Model Evaluation Module
Plots and prints all evaluation artefacts.
"""

import os
import logging
from typing import List

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_auc_score, roc_curve, classification_report,
    confusion_matrix, ConfusionMatrixDisplay, average_precision_score
)
from sklearn.model_selection import cross_val_score

from .config import LOCAL_OUTPUT_DIR, CV_FOLDS

log = logging.getLogger("alumni_pipeline")


class ModelEvaluator:
    """Plots and prints all evaluation artefacts. Saves to LOCAL_OUTPUT_DIR."""

    def run(self, X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble, feature_cols: List[str]) -> None:
        log.info("=== MODEL EVALUATION ===")
        self._print_classification_reports(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble)
        self._plot_roc_curves(X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble)
        self._plot_feature_importances(xgb_mdl, cat_mdl, baseline, feature_cols)
        self._plot_score_distributions(X_test, y_test, ensemble)
        self._cross_val_summary(X_test, y_test, baseline, xgb_mdl, cat_mdl, feature_cols)

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
            print(classification_report(y_test, pred, target_names=["Won't Donate", "Will Donate"]))

    def _plot_roc_curves(self, X_test, y_test, baseline, xgb_mdl, cat_mdl, ensemble):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        models = {
            "Logistic Regression": (baseline.predict_proba(X_test), "royalblue", "--"),
            "XGBoost"            : (xgb_mdl.predict_proba(X_test),  "darkorange", "-"),
            "CatBoost"           : (cat_mdl.predict_proba(X_test),  "forestgreen", "-"),
            "Ensemble"           : (ensemble.score(X_test),          "crimson", "-"),
        }

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

    def _plot_score_distributions(self, X_test, y_test, ensemble):
        scores = ensemble.score(X_test)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        ax = axes[0]
        ax.hist(scores[y_test == 0], bins=30, alpha=0.6, color="steelblue", label="Won't Donate")
        ax.hist(scores[y_test == 1], bins=30, alpha=0.6, color="tomato", label="Will Donate")
        ax.set_xlabel("Ensemble Score")
        ax.set_ylabel("Count")
        ax.set_title("Score Distribution by Class")
        ax.legend()

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

    @staticmethod
    def _cross_val_summary(X_test, y_test, baseline, xgb_mdl, cat_mdl, feature_cols):
        print("\n  Cross-Validation AUC (5-fold on test set — approximate):")
        lr_scores = cross_val_score(
            baseline.pipeline, X_test, y_test,
            cv=min(CV_FOLDS, len(X_test) // 10),
            scoring="roc_auc"
        )
        print(f"    Logistic Regression  :  {lr_scores.mean():.4f} ± {lr_scores.std():.4f}")
