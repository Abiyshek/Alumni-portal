"""
Complete Examples: AWS Integration & Security
Demonstrates how to use all new CPPE components.
"""

# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Using AWS S3 Storage
# ════════════════════════════════════════════════════════════════════════════════

from alumni_ml_pipeline.s3_storage import S3DataStore, get_s3_store
import pandas as pd

def example_s3_operations():
    """Upload and download data from S3."""
    
    # Initialize S3 store (local mode for demo)
    store = get_s3_store("alumni-raw-data", use_local=True)
    
    # Create sample data
    alumni_data = pd.DataFrame({
        "alumni_id": ["ALUM001", "ALUM002", "ALUM003"],
        "name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "email": ["john@alumni.edu", "jane@alumni.edu", "bob@alumni.edu"],
        "donation_amount": [250.00, 500.00, 150.00]
    })
    
    # Upload CSV to S3
    print("📤 Uploading CSV to S3...")
    store.put_csv("alumni/data/2026-02-16/alumni_data.csv", alumni_data)
    
    # Download CSV from S3
    print("📥 Downloading CSV from S3...")
    downloaded_df = store.get_csv("alumni/data/2026-02-16/alumni_data.csv")
    print(downloaded_df.head())
    
    # Upload JSON data
    import json
    json_data = {
        "metadata": {
            "total_alumni": 291,
            "last_updated": "2026-02-16",
            "version": "3.0"
        }
    }
    store.put_json("alumni/metadata/pipeline_info.json", json_data)
    
    # List all objects with prefix
    files = store.list_objects(prefix="alumni/data/")
    print(f"Files in S3: {files}")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Using RBAC (Role-Based Access Control)
# ════════════════════════════════════════════════════════════════════════════════

from alumni_ml_pipeline.rbac import (
    rbac_manager, Role, Permission, initialize_default_users
)

def example_rbac_access_control():
    """Demonstrate role-based access control."""
    
    # Initialize default users
    initialize_default_users()
    
    # Get users
    admin = rbac_manager.get_user("admin-001")
    officer = rbac_manager.get_user("officer-001")
    analyst = rbac_manager.get_user("analyst-001")
    viewer = rbac_manager.get_user("viewer-001")
    
    print("\n" + "="*70)
    print("ROLE-BASED ACCESS CONTROL EXAMPLES")
    print("="*70)
    
    # Test permissions
    permissions_to_check = [
        (Permission.VIEW_ALUMNI_DATA, "View alumni data"),
        (Permission.EDIT_ALUMNI_DATA, "Edit alumni data"),
        (Permission.EXPORT_DONATIONS, "Export donation data"),
        (Permission.MANAGE_USERS, "Manage users"),
    ]
    
    users = [admin, officer, analyst, viewer]
    users_info = ["Admin", "Alumni Officer", "Data Analyst", "Viewer"]
    
    for user, user_name in zip(users, users_info):
        print(f"\n👤 {user_name:20} ({user.username})")
        print("-" * 70)
        
        for permission, permission_name in permissions_to_check:
            has_access = user.has_permission(permission)
            status = "✅ ALLOW" if has_access else "❌ DENY"
            print(f"  {status:10}  {permission_name:30}  ({permission.value})")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Using Data Encryption
# ════════════════════════════════════════════════════════════════════════════════

from alumni_ml_pipeline.security import DataEncryption, FieldMasking

def example_encryption_and_masking():
    """Encrypt and mask sensitive data."""
    
    print("\n" + "="*70)
    print("DATA ENCRYPTION & MASKING EXAMPLES")
    print("="*70)
    
    # Initialize encryption (local mode)
    encryption = DataEncryption(use_kms=False)
    
    # Sample data
    sample_data = {
        "alumni_id": "ALUM001",
        "name": "John Doe",
        "email": "john.doe@alumni.edu",
        "phone": "5551234567",
        "ssn": "123-45-6789",
        "donation_amount": 250.00,
        "total_donations": 1500.00
    }
    
    print("\n📋 Original Data:")
    print("-" * 70)
    for key, value in sample_data.items():
        print(f"  {key:20} : {value}")
    
    # Encrypt sensitive fields
    print("\n🔐 ENCRYPTING Sensitive Fields:")
    print("-" * 70)
    encrypted_row = encryption.encrypt_row(sample_data)
    for key, value in encrypted_row.items():
        if key in ["email", "phone", "ssn", "donation_amount", "total_donations"]:
            print(f"  {key:20} : {value[:50]}...")  # Show first 50 chars
    
    # Decrypt
    print("\n🔓 DECRYPTING:")
    print("-" * 70)
    decrypted_row = encryption.decrypt_row(encrypted_row)
    email = decrypted_row["email"]
    phone = decrypted_row["phone"]
    print(f"  Email decrypted: {email}")
    print(f"  Phone decrypted: {phone}")
    
    # Mask for safe logging
    print("\n📝 MASKING for Safe Logging:")
    print("-" * 70)
    masked = FieldMasking.mask_dict_for_logging(sample_data)
    for key, value in masked.items():
        print(f"  {key:20} : {value}")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Using Audit Logging
# ════════════════════════════════════════════════════════════════════════════════

from alumni_ml_pipeline.enhanced_audit import audit_logger

def example_audit_logging():
    """Log various events for compliance."""
    
    print("\n" + "="*70)
    print("AUDIT LOGGING EXAMPLES")
    print("="*70)
    
    # Log data access
    print("\n📊 Log Data Access Event:")
    audit_logger.log_data_access(
        user_id="analyst-001",
        resource="alumni_data",
        action="Query donation history",
        row_count=145
    )
    
    # Log data export
    print("📤 Log Data Export Event (Compliance Critical):")
    audit_logger.log_data_export(
        user_id="finance-001",
        resource="alumni_scores",
        export_format="CSV",
        record_count=291
    )
    
    # Log model scoring
    print("🤖 Log Model Scoring Event:")
    audit_logger.log_model_scoring(
        model_version="v3.0-ensemble",
        alumni_scored=291,
        status="success"
    )
    
    # Log error
    print("❌ Log Error Event (Permission Denied):")
    audit_logger.log_error(
        event_type="access_denied",
        user_id="viewer-001",
        action="Attempt to export sensitive data",
        resource="alumni_passwords",
        error_message="User lacks permission: MANAGE_USERS"
    )
    
    print("\n✅ All audit events logged to: ./output/audit_trail.jsonl")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: Using Lambda Handlers
# ════════════════════════════════════════════════════════════════════════════════

from alumni_ml_pipeline.lambda_handlers import (
    lambda_ingest_engagement,
    lambda_ingest_donation,
    lambda_score_alumni,
    LambdaContext
)
import json

def example_lambda_invocations():
    """Test Lambda functions locally."""
    
    print("\n" + "="*70)
    print("LAMBDA FUNCTION EXAMPLES")
    print("="*70)
    
    context = LambdaContext()
    
    # Test engagement ingestion
    print("\n📌 Lambda: Ingest Engagement")
    print("-" * 70)
    engagement_event = {
        "body": json.dumps({
            "alumni_id": "ALUM001",
            "event_type": "attendance",
            "data": {
                "event_name": "Homecoming 2026",
                "location": "Boston, MA"
            }
        })
    }
    response = lambda_ingest_engagement(engagement_event, context)
    print(f"Status: {response['statusCode']}")
    print(f"Response: {response['body']}")
    
    # Test donation ingestion
    print("\n💳 Lambda: Ingest Donation (Encrypted)")
    print("-" * 70)
    donation_event = {
        "body": json.dumps({
            "alumni_id": "ALUM001",
            "amount": 250.00,
            "fund_type": "scholarship"
        })
    }
    response = lambda_ingest_donation(donation_event, context)
    print(f"Status: {response['statusCode']}")
    print(f"Response: {response['body']}")
    
    # Test scoring
    print("\n🎯 Lambda: Score Alumni")
    print("-" * 70)
    scoring_event = {}
    response = lambda_score_alumni(scoring_event, context)
    print(f"Status: {response['statusCode']}")
    print(f"Response: {response['body']}")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 6: Complete Pipeline with AWS Integration
# ════════════════════════════════════════════════════════════════════════════════

def example_complete_pipeline_with_aws():
    """Run complete pipeline with AWS integration enabled."""
    
    print("\n" + "="*70)
    print("COMPLETE PIPELINE WITH AWS INTEGRATION")
    print("="*70)
    
    from alumni_ml_pipeline.main import main
    
    # Run as Different Users with Different Permissions
    users = [
        ("admin-001", "Administrator", True),
        ("officer-001", "Alumni Officer", True),
        ("analyst-001", "Data Analyst", False),
    ]
    
    for user_id, user_name, use_aws in users:
        print(f"\n👤 Running as: {user_name}")
        print("="*70)
        
        try:
            context, data, scores = main(user_id=user_id, use_aws=use_aws)
            if context:
                print(f"✅ Pipeline completed successfully")
                print(f"   Alumni scored: {context['n_alumni_scored']}")
                print(f"   Ensemble AUC: {context['ensemble_auc']:.4f}")
            else:
                print(f"❌ Pipeline failed: Insufficient permissions or error")
        except Exception as e:
            print(f"❌ Error: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# EXAMPLE 7: Using GenAI with Context
# ════════════════════════════════════════════════════════════════════════════════

def example_genai_insights():
    """Generate insights using Claude GenAI."""
    
    from alumni_ml_pipeline.genai import GenAIInsightLayer
    
    print("\n" + "="*70)
    print("GENAI INSIGHTS EXAMPLES")
    print("="*70)
    
    # ModelContext from pipeline
    context = {
        "baseline_auc": 0.9747,
        "xgb_auc": 0.9644,
        "catboost_auc": 0.9632,
        "ensemble_auc": 0.9655,
        "top_feature": "engagement_score",
        "n_alumni_scored": 291,
        "n_train": 232,
        "n_test": 59,
        "positive_rate_train": 0.4957,
        "high_propensity_pct": 35.4,
    }
    
    genai = GenAIInsightLayer()
    
    # Generate business insights (with fallback)
    print("\n🤖 Generating Business Insights...")
    print("-" * 70)
    genai.run_insight_queries(context)


# ════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█  ALUMNI ML PIPELINE - CPPE IMPLEMENTATION EXAMPLES")
    print("█"*70)
    
    # Run examples
    print("\n[1] S3 Storage Operations")
    example_s3_operations()
    
    print("\n\n[2] Role-Based Access Control")
    example_rbac_access_control()
    
    print("\n\n[3] Encryption & Masking")
    example_encryption_and_masking()
    
    print("\n\n[4] Audit Logging")
    example_audit_logging()
    
    print("\n\n[5] Lambda Functions")
    example_lambda_invocations()
    
    print("\n\n[6] Complete Pipeline with AWS")
    example_complete_pipeline_with_aws()
    
    print("\n\n[7] GenAI Insights")
    example_genai_insights()
    
    print("\n" + "="*70)
    print("✅ ALL EXAMPLES COMPLETED")
    print("="*70)
    print("\n📚 See documentation:")
    print("   - AWS_DEPLOYMENT_GUIDE.md")
    print("   - SECURITY_IMPLEMENTATION.md")
    print("   - CPPE_IMPLEMENTATION.md")
    print("="*70)
