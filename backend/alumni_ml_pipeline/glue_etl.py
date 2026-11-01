"""
AWS Glue PySpark ETL Job Template
For large-scale data processing.

Note: AWS Glue modules are only available in AWS Glue runtime.
For local development, this module is a template reference only.
"""

import sys
import json
from datetime import datetime
import logging

log = logging.getLogger("alumni_pipeline")

# Optional imports - only available in AWS Glue runtime
try:
    from awsglue.transforms import *
    from awsglue.utils import getResolvedOptions
    from pyspark.context import SparkContext
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from awsglue.dynamicframe import DynamicFrame
    GLUE_AVAILABLE = True
except ImportError:
    GLUE_AVAILABLE = False
    log.debug("AWS Glue not available (expected in local development)")


def process_engagement_data(glue_context, input_path, output_path):
    """
    Glue job to process engagement data from S3.
    Reads raw engagement events and aggregates them by alumni.
    """
    if not GLUE_AVAILABLE:
        log.error("Spark not available for local processing")
        return None
    
    print(f"[Glue ETL] Processing engagement data from {input_path}")

    # Read JSON data from S3
    dynamic_frame = glue_context.create_dynamic_frame.from_options(
        format_options={"multiline": False},
        connection_type="s3",
        format="json",
        connection_options={"paths": [input_path]},
        transformation_ctx="source_data"
    )

    # Convert to Spark DataFrame for processing
    df = dynamic_frame.toDF()

    # Transformations
    df_aggregated = df \
        .groupBy("alumni_id") \
        .agg({
            "event_type": "count",
            "timestamp": "max"
        }) \
        .withColumnRenamed("count(event_type)", "total_events") \
        .withColumnRenamed("max(timestamp)", "last_event_date")

    # Add processing timestamp
    from pyspark.sql.functions import current_timestamp
    df_processed = df_aggregated.withColumn("processed_at", current_timestamp())

    # Write to S3 (Parquet format for efficiency)
    df_processed.write.mode("overwrite").parquet(output_path)
    print(f"[Glue ETL] ✓ Output written to {output_path}")

    return df_processed


def process_donation_data(glue_context, input_path, output_path):
    """
    Glue job to process donation data.
    Aggregates donations by alumni and fund type.
    """
    if not GLUE_AVAILABLE:
        log.error("Spark not available for local processing")
        return None
    
    print(f"[Glue ETL] Processing donation data from {input_path}")

    # Read data
    dynamic_frame = glue_context.create_dynamic_frame.from_options(
        connection_type="s3",
        format="json",
        connection_options={"paths": [input_path]},
        transformation_ctx="donation_data"
    )

    df = dynamic_frame.toDF()

    # Aggregate donations
    from pyspark.sql.functions import sum as spark_sum
    df_agg = df \
        .groupBy("alumni_id", "fund_type") \
        .agg(
            spark_sum("amount").alias("total_amount"),
            spark_sum("count(*)").alias("donation_count")
        )

    # Write output
    df_agg.write.mode("overwrite").parquet(output_path)
    print(f"[Glue ETL] ✓ Output written to {output_path}")

    return df_agg


def main():
    """Main Glue job execution."""
    if not GLUE_AVAILABLE:
        log.error("AWS Glue runtime not available. This module must run on AWS Glue.")
        log.info("For local development, use the pipeline without Glue integration.")
        return
    
    # Get job parameters
    args = getResolvedOptions(sys.argv, [
        "JOB_NAME",
        "S3_INPUT_BUCKET",
        "S3_OUTPUT_BUCKET",
    ])

    print(f"[Glue ETL] Starting job: {args['JOB_NAME']}")

    # Initialize Glue context
    try:
        sc = SparkContext()
        glue_context = GlueContext(sc)
        job = Job(glue_context)
        job.init(args["JOB_NAME"], args)
    except Exception as e:
        log.error(f"Failed to initialize Spark/Glue context: {e}")
        return

    try:
        # Process engagement data
        process_engagement_data(
            glue_context,
            f"s3://{args['S3_INPUT_BUCKET']}/raw/engagement/",
            f"s3://{args['S3_OUTPUT_BUCKET']}/processed/engagement_agg/"
        )

        # Process donation data
        process_donation_data(
            glue_context,
            f"s3://{args['S3_INPUT_BUCKET']}/raw/donations/",
            f"s3://{args['S3_OUTPUT_BUCKET']}/processed/donations_agg/"
        )

        print("[Glue ETL] ✓ Job completed successfully")
        job.commit()

    except Exception as e:
        print(f"[Glue ETL] ✗ Job failed: {e}")
        raise


if __name__ == "__main__":
    main()


# ── Deployment Instructions ──────────────────────────────────────────────────
"""
To deploy this Glue job:

1. Save this file as 'alumni_etl_job.py'

2. Upload to S3:
   aws s3 cp alumni_etl_job.py s3://alumni-ml-models/glue-scripts/

3. Create Glue job in AWS Console:
   - Name: alumni-etl-job
   - Type: Spark
   - Glue version: 3.0
   - Worker type: G.2X
   - Number of workers: 10
   - Script location: s3://alumni-ml-models/glue-scripts/alumni_etl_job.py
   - IAM role: alumni-glue-execution

4. Trigger options:
   - EventBridge schedule: Daily at 2 AM
   - Manual trigger
   - S3 event notification (new data arrival)

5. Monitor:
   - CloudWatch Logs: /aws/glue/jobs/alumni-etl-job
   - Glue Console: Jobs → Run history
"""
