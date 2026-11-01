#!/usr/bin/env python
"""
Quick Pipeline Runner - Works locally and with AWS
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("  ALUMNI ML PIPELINE - QUICK START")
print("=" * 70)

# Check if real AWS credentials are set
aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
use_aws = False

if aws_key and not aws_key.startswith("AKIA") or aws_key == "AKIAIOSFODNN7EXAMPLE":
    print("\n⚠️  Using LOCAL mode (example AWS credentials detected)")
    print("\nTo use REAL AWS:")
    print("  1. Go to AWS IAM → Users → admin-001 → Security credentials")
    print("  2. Create access key")
    print("  3. Update .env file with your REAL credentials:")
    print("     AWS_ACCESS_KEY_ID=AKIA...")
    print("     AWS_SECRET_ACCESS_KEY=wJal...")
    use_aws = False
else:
    print("\n✓ Using AWS mode")
    use_aws = True

print(f"\n[Running Pipeline] {'with AWS' if use_aws else 'LOCAL MODE'}\n")

from alumni_ml_pipeline.main import main

# Run pipeline
context, data, scores = main(user_id='admin-001', use_aws=use_aws)

# Summary
print("\n" + "=" * 70)
print("  ✓ PIPELINE COMPLETE")
print("=" * 70)
print(f"\n  Alumni scored         : {len(data):,}")
print(f"  Logistic Regression   : {context.get('baseline_auc', 'N/A'):.4f}")
print(f"  XGBoost               : {context.get('xgb_auc', 'N/A'):.4f}")
print(f"  CatBoost              : {context.get('catboost_auc', 'N/A'):.4f}")
print(f"  Ensemble              : {context.get('ensemble_auc', 'N/A'):.4f}")
print(f"  High-propensity       : {context.get('high_propensity_pct', 'N/A')}%")
print(f"\n  Outputs saved to: G:/MINI_PROJECT/output/")
if use_aws:
    print(f"  Also uploaded to S3  : s3://alumni-data-lake/")
print("\n")
