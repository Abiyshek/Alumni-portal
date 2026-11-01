#!/usr/bin/env python
"""Add S3 permissions to user-alumni"""
import json
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION', 'us-east-1')

# Create IAM client with explicit credentials
iam = boto3.client(
    'iam',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# S3 policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketVersioning",
                "s3:PutBucketVersioning"
            ],
            "Resource": [
                "arn:aws:s3:::alumni-bucket2026",
                "arn:aws:s3:::alumni-bucket2026/*"
            ]
        }
    ]
}

try:
    # Attach policy to user
    iam.put_user_policy(
        UserName='user-alumni',
        PolicyName='alumni-s3-policy',
        PolicyDocument=json.dumps(policy)
    )
    print("✓ S3 permissions successfully added to user-alumni!")
    print("  Policy name: alumni-s3-policy")
    print("  Resources: arn:aws:s3:::alumni-bucket2026/*")
except ClientError as e:
    print(f"✗ Error: {e}")
