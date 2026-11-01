#!/usr/bin/env python
"""
Complete AWS Pipeline Runner
- Loads .env credentials
- Tests AWS/S3 connection
- Runs pipeline with AWS integration
- Verifies outputs in S3
"""

import os
import sys
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  AWS PIPELINE SETUP & EXECUTION")
print("=" * 70)

# Step 1: Check credentials
print("\n[1/4] Checking AWS Credentials...")
aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
aws_region = os.environ.get("AWS_REGION", "us-east-1")
s3_bucket = os.environ.get("AWS_S3_BUCKET", "alumni-data-lake")

if not aws_key or not aws_secret:
    print("  ✗ ERROR: AWS credentials not found in .env")
    print("  Please update .env with:")
    print("    AWS_ACCESS_KEY_ID=your_key")
    print("    AWS_SECRET_ACCESS_KEY=your_secret")
    sys.exit(1)

print(f"  ✓ AWS_ACCESS_KEY_ID: {aws_key[:20]}...")
print(f"  ✓ AWS_REGION: {aws_region}")
print(f"  ✓ S3_BUCKET: {s3_bucket}")

# Step 2: Test boto3 connection
print("\n[2/4] Testing S3 Connection...")
try:
    import boto3
    s3 = boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret
    )
    
    # Test specific bucket access instead of listing all buckets
    try:
        response = s3.head_bucket(Bucket=s3_bucket)
        print(f"  ✓ Connected to AWS")
        print(f"  ✓ Bucket '{s3_bucket}' accessible")
    except s3.exceptions.NoSuchBucket:
        print(f"  ⚠ Bucket '{s3_bucket}' not found. Attempting to create...")
        try:
            if aws_region == "us-east-1":
                s3.create_bucket(Bucket=s3_bucket)
            else:
                s3.create_bucket(
                    Bucket=s3_bucket,
                    CreateBucketConfiguration={'LocationConstraint': aws_region}
                )
            print(f"  ✓ Bucket '{s3_bucket}' created successfully")
        except Exception as create_err:
            print(f"  ✗ Could not create bucket: {create_err}")
            sys.exit(1)
        
except Exception as e:
    print(f"  ✗ S3 Connection Error: {e}")
    print(f"  Check your AWS credentials in .env")
    sys.exit(1)

# Step 3: Run Pipeline
print("\n[3/4] Running ML Pipeline with AWS Integration...")
print("-" * 70)
try:
    from alumni_ml_pipeline.main import main
    
    context, data, scores = main(user_id='admin-001', use_aws=True)
    
    print("-" * 70)
    print("  ✓ Pipeline executed successfully")
except Exception as e:
    print(f"  ✗ Pipeline Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Verify S3 outputs
print("\n[4/4] Verifying S3 Outputs...")
try:
    response = s3.list_objects_v2(Bucket=s3_bucket)
    
    if 'Contents' not in response:
        print(f"  ⚠ No files in S3 bucket (local mode may have been used)")
    else:
        files = response['Contents']
        print(f"  ✓ Found {len(files)} files in S3:")
        for obj in files:
            size_mb = obj['Size'] / 1024 / 1024
            print(f"    - {obj['Key']} ({size_mb:.2f} MB)")
except Exception as e:
    print(f"  ✗ Error listing S3 files: {e}")

print("\n" + "=" * 70)
print("  ✓ PIPELINE COMPLETE")
print("=" * 70)
print(f"\n  Results Summary:")
print(f"    Alumni scored: {len(data):,}")
print(f"    Ensemble AUC: {context.get('ensemble_auc', 'N/A')}")
print(f"    High-propensity: {context.get('high_propensity_pct', 'N/A')}%")
print(f"    S3 Bucket: s3://{s3_bucket}/")
print("\n")
