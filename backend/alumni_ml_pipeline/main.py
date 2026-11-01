"""
Main Orchestrator Module
Coordinates all pipeline components with AWS integration.
Enhanced with RBAC, encryption, and audit logging.
"""

import os
import logging
import warnings
import numpy as np

from .config import (
    LOCAL_OUTPUT_DIR, LOCAL_INPUT_DIR, RANDOM_SEED,
    FEATURE_COLS
)
from .data_loader import DataLoader
from .eda import EDASummary
from .features import FeatureEngineer, prepare_train_test
from .models import BaselineModel, XGBoostModel, CatBoostModel
from .ensemble import EnsembleScorer
from .evaluation import ModelEvaluator
from .genai import GenAIInsightLayer
from .audit import write_audit_log
from .enhanced_audit import write_enhanced_audit_log, audit_logger
from .rbac import rbac_manager, Permission, initialize_default_users
from .s3_storage import S3DataStore
from .security import DataEncryption

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("alumni_pipeline")

warnings.filterwarnings("ignore")
np.random.seed(RANDOM_SEED)


def main(user_id: str = "system", use_aws: bool = False):
    print("=" * 70)
    print("  ALUMNI DONATION & ENGAGEMENT PREDICTION SYSTEM  v3.0.0")
    print("  AWS-Compatible Production ML Pipeline with RBAC & Encryption")
    print("=" * 70)

    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    # ── Initialize RBAC ───────────────────────────────────────────────────────
    initialize_default_users()
    user = rbac_manager.get_user(user_id)
    if not user:
        log.warning(f"User {user_id} not found, using system account")
        user_id = "system"
    
    # Check permission
    if not rbac_manager.check_access(user_id, Permission.GENERATE_REPORTS):
        log.error(f"✗ User {user_id} lacks permission to run pipeline")
        return None, None, None
    
    log.info(f"✓ User authenticated: {user_id}")
    
    # Log pipeline start
    audit_logger.log_event(
        event_type="pipeline_start",
        user_id=user_id,
        action="Start alumni pipeline",
        resource="ml_pipeline",
        status="started"
    )
    
    # Initialize AWS services if requested
    s3_store = None
    encryption = None
    if use_aws:
        try:
            bucket_name = os.environ.get("AWS_S3_BUCKET", "alumni-data-lake")
            s3_store = S3DataStore(bucket_name, use_local=False)  # Use REAL AWS S3
            encryption = DataEncryption(use_kms=False)
            log.info(f"✓ AWS services initialized → s3://{bucket_name}/")
        except Exception as e:
            log.warning(f"AWS initialization failed: {e}. Falling back to local storage.")
            s3_store = S3DataStore("alumni-raw-data", use_local=True)
    
    # ── [1] Data Loading ──────────────────────────────────────────────────────
    loader = DataLoader(use_s3=False, local_dir=LOCAL_INPUT_DIR)
    raw    = loader.load_all()
    
    # Log data access
    audit_logger.log_data_access(
        user_id=user_id,
        resource="alumni_data",
        action="Load training data",
        row_count=len(raw)
    )

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
    cat_cols = []
    cat_mdl  = CatBoostModel(cat_features=cat_cols)
    cat_mdl.train(X_train, y_train)
    cat_auc = cat_mdl.evaluate(X_test, y_test)

    # ── [7] Ensemble Scoring ────

    # ── [7] Ensemble Scoring ──────────────────────────────────────────────
    ensemble    = EnsembleScorer(xgb_mdl, cat_mdl)
    ens_scores  = ensemble.score(X_test, y_test)
    ens_auc     = ensemble.auc or 0.0

    # Write full-dataset scores (all alumni) back to "S3"
    import pandas as pd
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
        if xgb_mdl.model is not None
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
    }
    genai = GenAIInsightLayer()
    genai.run_insight_queries(model_context)

    # ── [10] Audit Logging ────────────────────────────────────────────────────
    write_audit_log(model_context)
    write_enhanced_audit_log(model_context, user_id)
    
    # Log model scoring
    audit_logger.log_model_scoring(
        model_version="v3.0-ensemble",
        alumni_scored=len(data),
        status="success"
    )
    
    # Log data export
    audit_logger.log_data_export(
        user_id=user_id,
        resource="alumni_scores",
        export_format="CSV",
        record_count=len(data),
        status="success"
    )

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  User authenticated      : {user_id}")
    print(f"  AWS integration         : {'Enabled (uploading to S3)' if use_aws else 'Disabled'}")
    print(f"  Alumni scored           : {len(data):,}")
    print(f"  Logistic Regression AUC : {lr_auc:.4f}")
    print(f"  XGBoost AUC             : {xgb_auc:.4f}")
    print(f"  CatBoost AUC            : {cat_auc:.4f}")
    print(f"  Ensemble AUC            : {ens_auc:.4f}")
    print(f"  High-propensity alumni  : {model_context['high_propensity_pct']}%  (score > 0.70)")
    print(f"\n  Outputs saved to:")
    print(f"    {LOCAL_OUTPUT_DIR}01_eda_summary.png")
    print(f"    {LOCAL_OUTPUT_DIR}02_roc_curves.png")
    print(f"    {LOCAL_OUTPUT_DIR}03_feature_importance.png")
    print(f"    {LOCAL_OUTPUT_DIR}04_score_distributions.png")
    print(f"    {LOCAL_OUTPUT_DIR}alumni_scores.csv")
    print(f"    {LOCAL_OUTPUT_DIR}audit_log.json")
    print(f"    {LOCAL_OUTPUT_DIR}audit_trail.jsonl  (compliance)")
    
    # Upload files to S3 if AWS is enabled
    if use_aws and s3_store:
        print(f"\n  Uploading to S3:")
        files_to_upload = [
            ("01_eda_summary.png", "images/"),
            ("02_roc_curves.png", "images/"),
            ("03_feature_importance.png", "images/"),
            ("04_score_distributions.png", "images/"),
            ("alumni_scores.csv", "scores/"),
            ("audit_log.json", "audit/"),
            ("audit_trail.jsonl", "audit/"),
        ]
        
        for filename, subfolder in files_to_upload:
            local_path = f"{LOCAL_OUTPUT_DIR}{filename}"
            if os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    s3_key = f"{subfolder}{filename}"
                    s3_store.put_object(s3_key, f.read())
                    print(f"    ✓ {filename} → s3://{s3_store.bucket}/{s3_key}")
    
    print("=" * 70)

    return model_context, data, all_scores


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    context, scored_data, scores = main(user_id="admin-001", use_aws=False)
