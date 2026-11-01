#!/usr/bin/env python
"""Verify S3 bucket contents"""
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get credentials and bucket from .env
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION', 'us-east-1')
bucket_name = os.getenv('AWS_S3_BUCKET')

# Create S3 client with explicit credentials
s3 = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

try:
    response = s3.list_objects_v2(Bucket=bucket_name)
    print(f'✓ Files in S3 bucket ({bucket_name}):\n')
    if 'Contents' in response:
        total_size = 0
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            total_size += obj['Size']
            print(f'  {obj["Key"]:50} {size_kb:10.1f} KB')
        print(f'\n  Total: {len(response["Contents"])} files, {total_size/1024/1024:.2f} MB')
    else:
        print('  (empty)')
except Exception as e:
    print(f'✗ Error: {str(e)}')
