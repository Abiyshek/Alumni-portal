"""
USAGE EXAMPLES: Alumni ML Pipeline Modules
============================================

This file demonstrates how to use each module independently or together.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 1: Run Complete Pipeline (Simplest)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Simply run:
    python run_pipeline.py

Or from Python:
"""
from alumni_ml_pipeline.main import main

context, scored_data, scores = main()
print(f"✓ Pipeline complete! Ensemble AUC: {context['ensemble_auc']}")
print(f"  Alumni scored: {context['n_alumni_scored']}")
print(f"  High-propensity alumni: {context['high_propensity_pct']}%")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 2: Data Loading Only
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.data_loader import DataLoader
from alumni_ml_pipeline.config import LOCAL_INPUT_DIR

# Load all datasets
loader = DataLoader(use_s3=False, local_dir=LOCAL_INPUT_DIR)
raw_data = loader.load_all()

# Inspect loaded data
for dataset_name, df in raw_data.items():
    print(f"{dataset_name}: {len(df)} rows × {df.shape[1]} cols")

# Access specific dataset
alumni_df = raw_data.get("alumni_people")
if alumni_df is not None:
    print(f"Alumni: {alumni_df.head()}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 3: EDA Analysis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.eda import EDASummary

eda = EDASummary()
eda.run(raw_data)  # Generates 01_eda_summary.png


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 4: Feature Engineering
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.features import FeatureEngineer, prepare_train_test

# Build feature matrix
engineer = FeatureEngineer(raw_data, n_synthetic=1000)
feature_matrix = engineer.build()

print(f"Feature matrix shape: {feature_matrix.shape}")
print(f"Columns: {list(feature_matrix.columns)}")

# Split into train/test
X_train, X_test, y_train, y_test, feature_cols = prepare_train_test(feature_matrix)

print(f"Train set: {len(X_train)} rows")
print(f"Test set: {len(X_test)} rows")
print(f"Features used: {len(feature_cols)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 5: Train Individual Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.models import BaselineModel, XGBoostModel, CatBoostModel

# === Baseline (Logistic Regression) ===
print("\n--- Training Baseline Model ---")
baseline = BaselineModel()
baseline.train(X_train, y_train)
lr_auc = baseline.evaluate(X_test, y_test)
print(f"Baseline AUC: {lr_auc:.4f}")

# Check feature importance
print("\nTop features (by coefficient magnitude):")
print(baseline.coef_df.head(5))

# === XGBoost ===
print("\n--- Training XGBoost Model ---")
xgb = XGBoostModel()
xgb.train(X_train, y_train)
xgb_auc = xgb.evaluate(X_test, y_test)
print(f"XGBoost AUC: {xgb_auc:.4f}")

# Feature importance
if xgb.model is not None:
    print("\nTop features (by importance):")
    print(xgb.feature_importance(feature_cols).head(5))

# === CatBoost ===
print("\n--- Training CatBoost Model ---")
catboost = CatBoostModel()
catboost.train(X_train, y_train)
cat_auc = catboost.evaluate(X_test, y_test)
print(f"CatBoost AUC: {cat_auc:.4f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 6: Ensemble Scoring
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.ensemble import EnsembleScorer

# Create ensemble (0.55 XGBoost + 0.45 CatBoost)
ensemble = EnsembleScorer(xgb, catboost)

# Score test set
scores = ensemble.score(X_test, y=y_test)

print(f"\nEnsemble AUC: {ensemble.auc:.4f}")
print(f"Score range: [{scores.min():.3f}, {scores.max():.3f}]")
print(f"Mean score: {scores.mean():.3f}")

# Score all data for production
all_scores = ensemble.score(feature_matrix[feature_cols].fillna(feature_matrix[feature_cols].median()))
ensemble.write_scores_to_s3(feature_matrix, all_scores)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 7: Model Evaluation (Detailed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.evaluation import ModelEvaluator

evaluator = ModelEvaluator()
evaluator.run(
    X_test, y_test,
    baseline, xgb, catboost, ensemble,
    feature_cols
)
# Generates:
# - 02_roc_curves.png
# - 03_feature_importance.png
# - 04_score_distributions.png


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 8: GenAI Insights
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.genai import GenAIInsightLayer

# Create context from model results
model_context = {
    "baseline_auc": round(lr_auc, 4),
    "xgb_auc": round(xgb_auc, 4),
    "catboost_auc": round(cat_auc, 4),
    "ensemble_auc": round(ensemble.auc or 0.0, 4),
    "n_alumni_scored": len(feature_matrix),
    "high_propensity_pct": round((all_scores > 0.7).mean() * 100, 1),
}

# Generate insights
genai = GenAIInsightLayer()

# Option 1: Run all canonical queries
genai.run_insight_queries(model_context)

# Option 2: Ask custom question (requires ANTHROPIC_API_KEY env var)
answer = genai.ask(
    "What is the relationship between engagement score and donation probability?",
    model_context
)
print(f"\nGenAI Answer:\n{answer}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 9: Audit Logging
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from alumni_ml_pipeline.audit import write_audit_log

audit_record = {
    "model_version": "2.0.0",
    "pipeline_date": "2026-02-16",
    "baseline_auc": round(lr_auc, 4),
    "ensemble_auc": round(ensemble.auc or 0.0, 4),
    "n_alumni_scored": len(feature_matrix),
    "donation_amount": 50000,  # Will be hashed for security
    "email": "test@alumni.edu",  # Will be hashed
}

write_audit_log(audit_record)
# Generates: audit_log.json (with sensitive fields hashed)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE 10: Custom Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Access/modify configuration
from alumni_ml_pipeline import config

print(f"Current random seed: {config.RANDOM_SEED}")
print(f"Test size: {config.TEST_SIZE}")
print(f"Ensemble weights: XGB={config.ENSEMBLE_W_XGB}, CAT={config.ENSEMBLE_W_CAT}")
print(f"Feature columns: {len(config.FEATURE_COLS)} features")
print(f"Target column: {config.TARGET_COL}")

# For development, you can modify:
# config.LOCAL_INPUT_DIR = "/custom/path/to/data"
# config.LOCAL_OUTPUT_DIR = "/custom/output/path"
# config.ENSEMBLE_W_XGB = 0.6
# config.ENSEMBLE_W_CAT = 0.4


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY OF MODULE DEPENDENCIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Data Flow:
   config.py ← used by all modules
       ↓
   main.py (orchestration)
       ├─→ data_loader.py → Raw data
       ├─→ eda.py → Summary stats
       ├─→ features.py → Feature matrix
       ├─→ models.py → Model predictions
       ├─→ ensemble.py → Ensemble scores
       ├─→ evaluation.py → Visualizations
       ├─→ genai.py → Insights
       └─→ audit.py → Compliance log

Independence:
   ✓ config.py has no dependencies (pure configuration)
   ✓ data_loader.py can run standalone
   ✓ eda.py requires only raw data
   ✓ features.py requires only raw data
   ✓ models.py requires only X_train, y_train, X_test, y_test
   ✓ ensemble.py requires trained models
   ✓ evaluation.py requires all models
   ✓ genai.py requires only model context dict
   ✓ audit.py requires only results dict

Testing Strategy:
   1. Test each module in isolation with mock data
   2. Integration test: Load → EDA → Features → Train → Evaluate
   3. End-to-end test: python run_pipeline.py
"""

print("\n✅ All examples completed successfully!")
print("For more details, see README.md and MIGRATION_GUIDE.md")
