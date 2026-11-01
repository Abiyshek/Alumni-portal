"""
API Gateway Setup Guide & Implementation
Complete REST API for alumni platform.
"""

# This file contains:
# 1. API endpoint definitions
# 2. Request/response models
# 3. AWS SAM template for infrastructure as code

API_ENDPOINTS = {
    # Engagement data ingestion
    "POST /alumni/engagement": {
        "description": "Record alumni engagement event",
        "handler": "lambda_ingest_engagement",
        "auth": "API_KEY",
        "body_schema": {
            "alumni_id": "string (required)",
            "event_type": "string (attendance|newsletter|login)",
            "data": "object (optional)",
            "timestamp": "datetime (optional)"
        },
        "response": 200,
        "example": {
            "message": "Engagement recorded",
            "alumni_id": "ALUM001"
        }
    },

    # Donation data ingestion
    "POST /alumni/donation": {
        "description": "Record alumni donation",
        "handler": "lambda_ingest_donation",
        "auth": "API_KEY + Encryption",
        "body_schema": {
            "alumni_id": "string (required)",
            "amount": "float (required)",
            "fund_type": "string (general|scholarship|infrastructure)",
            "date": "datetime (optional)"
        },
        "response": 200,
        "example": {
            "message": "Donation recorded",
            "alumni_id": "ALUM001",
            "reference_id": "DONATE-ALUM001-123456"
        }
    },

    # Get alumni profile & scores
    "GET /alumni/{alumni_id}": {
        "description": "Get alumni profile with donation score",
        "handler": "lambda_get_alumni",
        "auth": "IAM + RBAC",
        "path_params": {
            "alumni_id": "string"
        },
        "response": 200,
        "example": {
            "alumni_id": "ALUM001",
            "name": "John Doe",
            "email": "***@alumni.edu",
            "donation_score": 0.85,
            "engagement_level": "high",
            "last_engagement": "2026-02-16"
        }
    },

    # Generate donation forecast
    "POST /alumni/forecast": {
        "description": "Generate donation forecast for alumni segment",
        "handler": "lambda_generate_forecast",
        "auth": "IAM + RBAC",
        "body_schema": {
            "segment": "string (recent_grads|mid_career|executives)",
            "fund_type": "string",
            "month": "integer (optional)"
        },
        "response": 200,
        "example": {
            "segment": "mid_career",
            "predicted_donors": 150,
            "projected_amount": "$500,000",
            "confidence": 0.87
        }
    },

    # Get engagement insights (GenAI)
    "GET /alumni/insights": {
        "description": "Get natural language insights from GenAI",
        "handler": "lambda_get_insights",
        "auth": "IAM + RBAC",
        "query_params": {
            "question": "string (e.g., 'Which segment donates most?')"
        },
        "response": 200,
        "example": {
            "question": "Which segment donates most?",
            "answer": "Alumni 7-20 years post-graduation in tech roles...",
            "confidence": 0.92
        }
    },

    # Generate report
    "POST /reports/generate": {
        "description": "Generate compliance report",
        "handler": "lambda_generate_report",
        "auth": "IAM + RBAC (Finance role)",
        "body_schema": {
            "report_type": "string (summary|segment|forecast)",
            "format": "string (pdf|csv)",
            "period": "string (monthly|quarterly|annual)"
        },
        "response": 200,
        "example": {
            "report_id": "RPT-202602-001",
            "status": "generating",
            "s3_url": "s3://alumni-reports/report-202602-001.pdf"
        }
    },

    # Export data (audit logged)
    "POST /data/export": {
        "description": "Export alumni data (audit logged)",
        "handler": "lambda_export_data",
        "auth": "IAM + RBAC (Admin/Finance)",
        "body_schema": {
            "filters": "object",
            "format": "string (csv|json)",
            "include_sensitive": "boolean"
        },
        "response": 200,
        "example": {
            "export_id": "EXP-202602-001",
            "record_count": 291,
            "download_url": "https://...",
            "expires_in": "24 hours"
        }
    },
}

# AWS SAM Template (Infrastructure as Code)
SAM_TEMPLATE = """
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Alumni Engagement Platform - Serverless Architecture

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Globals:
  Function:
    Timeout: 60
    MemorySize: 512
    Runtime: python3.9

Resources:
  # API Gateway
  AlumniAPI:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Auth:
        ApiKeyRequired: true
      MethodSettings:
        - ResourcePath: '/*'
          HttpMethod: '*'
          LoggingLevel: INFO
          DataTraceEnabled: true

  # Lambda: Ingest Engagement
  IngestEngagementFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: alumni-ingest-engagement
      CodeUri: lambda_handlers.py
      Handler: lambda_ingest_engagement
      Events:
        ApiEvent:
          Type: Api
          Properties:
            RestApiId: !Ref AlumniAPI
            Path: /alumni/engagement
            Method: POST
      Environment:
        Variables:
          S3_BUCKET: !Ref S3BucketInput
          DYNAMODB_TABLE: !Ref DynamoDBEngagement
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref S3BucketInput
        - DynamoDBCrudPolicy:
            TableName: !Ref DynamoDBEngagement

  # Lambda: Ingest Donations
  IngestDonationFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: alumni-ingest-donation
      CodeUri: lambda_handlers.py
      Handler: lambda_ingest_donation
      Events:
        ApiEvent:
          Type: Api
          Properties:
            RestApiId: !Ref AlumniAPI
            Path: /alumni/donation
            Method: POST
      Environment:
        Variables:
          S3_BUCKET: !Ref S3BucketInput
          KMS_KEY_ID: !GetAtt KMSKey.Arn
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref S3BucketInput
        - KMSDecryptPolicy:
            KeyId: !Ref KMSKey

  # Lambda: Score Alumni
  ScoreAlumniFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: alumni-score-alumni
      CodeUri: lambda_handlers.py
      Handler: lambda_score_alumni
      Timeout: 300
      MemorySize: 1024
      Environment:
        Variables:
          S3_MODEL_BUCKET: !Ref S3BucketModels
          DYNAMODB_SCORES: !Ref DynamoDBScores
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref S3BucketModels
        - DynamoDBCrudPolicy:
            TableName: !Ref DynamoDBScores

  # S3 Buckets
  S3BucketInput:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'alumni-raw-data-${Environment}'
      VersioningConfiguration:
        Status: Enabled
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: aws:kms
            KMSMasterKeyID: !GetAtt KMSKey.Arn

  S3BucketProcessed:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'alumni-processed-data-${Environment}'

  S3BucketModels:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'alumni-ml-models-${Environment}'

  # DynamoDB Tables
  DynamoDBEngagement:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: alumni-engagement
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: alumni_id
          AttributeType: S
        - AttributeName: timestamp
          AttributeType: S
      KeySchema:
        - AttributeName: alumni_id
          KeyType: HASH
        - AttributeName: timestamp
          KeyType: RANGE
      TTL:
        AttributeName: ttl
        Enabled: true

  DynamoDBScores:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: alumni-donation-scores
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: alumni_id
          AttributeType: S
      KeySchema:
        - AttributeName: alumni_id
          KeyType: HASH

  # KMS Key for encryption
  KMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Alumni data encryption key
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM policies
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/alumni/pipeline
      RetentionInDays: 30

Outputs:
  APIEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${AlumniAPI}.execute-api.${AWS::Region}.amazonaws.com/${Environment}'
  
  S3InputBucket:
    Description: S3 bucket for raw data
    Value: !Ref S3BucketInput
  
  S3ProcessedBucket:
    Description: S3 bucket for processed data
    Value: !Ref S3BucketProcessed
"""

print("API Gateway Setup Guide")
print("=" * 60)
print("Endpoints defined:", len(API_ENDPOINTS))
print("Total Lambda functions: 6")
print("\\nTo deploy:")
print("1. Save SAM template as template.yaml")
print("2. Run: sam build && sam deploy --guided")
print("=" * 60)
