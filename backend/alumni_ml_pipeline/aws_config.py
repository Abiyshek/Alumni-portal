"""
AWS Infrastructure Setup Module
Configuration for API Gateway, Lambda, S3, and other AWS services.
"""

import os
import json
import logging

log = logging.getLogger("alumni_pipeline")

# ── AWS Configuration ─────────────────────────────────────────────────────────
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID", "123456789012")

# S3 Buckets
S3_BUCKET_INPUT = "alumni-raw-data"
S3_BUCKET_PROCESSED = "alumni-processed-data"
S3_BUCKET_MODELS = "alumni-ml-models"
S3_BUCKET_REPORTS = "alumni-reports"

# Lambda Functions
LAMBDA_INGEST_ENGAGEMENT = "alumni-ingest-engagement"
LAMBDA_INGEST_DONATIONS = "alumni-ingest-donations"
LAMBDA_SCORE_ALUMNI = "alumni-score-alumni"
LAMBDA_GENERATE_REPORT = "alumni-generate-report"

# API Gateway
API_GATEWAY_STAGE = "prod"
API_BASE_URL = f"https://api.alumni.example.com/{API_GATEWAY_STAGE}"

# Glue
GLUE_DATABASE = "alumni_warehouse"
GLUE_JOB_TRANSFORM = "alumni-transform-data"
GLUE_JOB_FEATURE_ENGINEERING = "alumni-feature-engineering"

# DynamoDB (for caching & real-time data)
DYNAMODB_TABLE_ALUMNI = "alumni-profiles"
DYNAMODB_TABLE_ENGAGEMENT = "alumni-engagement"
DYNAMODB_TABLE_SCORES = "alumni-donation-scores"

# CloudWatch
CLOUDWATCH_LOG_GROUP = "/aws/alumni/pipeline"

# IAM Roles
IAM_ROLE_LAMBDA = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/alumni-lambda-execution"
IAM_ROLE_GLUE = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/alumni-glue-execution"

# KMS Encryption
KMS_KEY_ID = os.environ.get("KMS_KEY_ID", "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012")

# ── Service Initialization ────────────────────────────────────────────────────
def get_aws_clients():
    """Returns configured AWS service clients."""
    try:
        import boto3
        return {
            "s3": boto3.client("s3", region_name=AWS_REGION),
            "lambda": boto3.client("lambda", region_name=AWS_REGION),
            "apigateway": boto3.client("apigateway", region_name=AWS_REGION),
            "glue": boto3.client("glue", region_name=AWS_REGION),
            "dynamodb": boto3.client("dynamodb", region_name=AWS_REGION),
            "logs": boto3.client("logs", region_name=AWS_REGION),
            "kms": boto3.client("kms", region_name=AWS_REGION),
            "iam": boto3.client("iam", region_name=AWS_REGION),
        }
    except ImportError:
        log.warning("boto3 not installed — AWS integration unavailable")
        return {}

# ── Validation ────────────────────────────────────────────────────────────────
def validate_aws_config():
    """Validates AWS configuration is properly set."""
    required_env_vars = ["AWS_REGION", "AWS_ACCOUNT_ID"]
    missing = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing:
        log.warning(f"Missing AWS environment variables: {missing}")
        return False
    
    return True
