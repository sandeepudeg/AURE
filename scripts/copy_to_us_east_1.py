#!/usr/bin/env python3
"""
Copy scheme PDFs to us-east-1 bucket for Bedrock KB
"""

import sys
import os
import logging
import boto3
from botocore.exceptions import ClientError

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.bedrock_kb_loader import BedrockKBLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_us_east_1_bucket(account_id: str) -> str:
    """Create S3 bucket in us-east-1"""
    bucket_name = f'ure-mvp-data-us-east-1-{account_id}'
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    try:
        # For us-east-1, don't specify LocationConstraint
        s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"✓ Created bucket: {bucket_name} in us-east-1")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            logger.info(f"✓ Bucket {bucket_name} already exists")
        else:
            raise
    
    return bucket_name


def copy_scheme_pdfs(source_bucket: str, dest_bucket: str, prefix: str = 'schemes/'):
    """Copy scheme PDFs from source to destination bucket"""
    s3_source = boto3.client('s3', region_name='ap-south-1')
    s3_dest = boto3.client('s3', region_name='us-east-1')
    
    logger.info(f"Copying files from {source_bucket}/{prefix} to {dest_bucket}/{prefix}")
    
    # List objects in source bucket
    response = s3_source.list_objects_v2(Bucket=source_bucket, Prefix=prefix)
    
    if 'Contents' not in response:
        logger.warning(f"No files found in {source_bucket}/{prefix}")
        return 0
    
    copied_count = 0
    for obj in response['Contents']:
        key = obj['Key']
        
        # Skip directory markers
        if key.endswith('/'):
            continue
        
        logger.info(f"  Copying: {key}")
        
        # Copy object
        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3_dest.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=key
        )
        copied_count += 1
    
    logger.info(f"✓ Copied {copied_count} files")
    return copied_count


def main():
    account_id = '188238313375'
    kb_id = '7XROZ6PZIF'
    source_bucket = f'ure-mvp-data-{account_id}'
    s3_prefix = 'schemes/'
    bedrock_role_arn = f'arn:aws:iam::{account_id}:role/BedrockKBRole-us-east-1-{account_id}'
    
    logger.info("=" * 60)
    logger.info("COPY SCHEME PDFs TO US-EAST-1")
    logger.info("=" * 60)
    
    # Step 1: Create us-east-1 bucket
    logger.info("\nStep 1: Creating S3 bucket in us-east-1")
    dest_bucket = create_us_east_1_bucket(account_id)
    
    # Step 2: Copy scheme PDFs
    logger.info("\nStep 2: Copying scheme PDFs")
    copied = copy_scheme_pdfs(source_bucket, dest_bucket, s3_prefix)
    
    if copied == 0:
        logger.error("No files copied. Exiting.")
        return
    
    # Step 3: Configure bucket policy
    logger.info("\nStep 3: Configuring S3 bucket policy")
    loader = BedrockKBLoader(region='us-east-1')
    loader.configure_s3_bucket_policy(dest_bucket, bedrock_role_arn)
    
    # Step 4: Create new data source
    logger.info(f"\nStep 4: Creating data source for KB: {kb_id}")
    data_source_id = loader.create_data_source(
        kb_id=kb_id,
        s3_bucket=dest_bucket,
        s3_prefix=s3_prefix,
        data_source_name='pm-kisan-docs-us-east-1'
    )
    
    if not data_source_id:
        logger.error("Failed to create data source")
        return
    
    logger.info(f"✓ Data source created: {data_source_id}")
    
    # Step 5: Start ingestion job
    logger.info(f"\nStep 5: Starting ingestion job")
    job_id = loader.start_ingestion_job(kb_id, data_source_id)
    
    if job_id:
        logger.info(f"\n{'=' * 60}")
        logger.info("SUCCESS!")
        logger.info(f"{'=' * 60}")
        logger.info(f"New bucket: {dest_bucket}")
        logger.info(f"Data source: {data_source_id}")
        logger.info(f"Ingestion job: {job_id}")
    else:
        logger.error("Failed to start ingestion job")


if __name__ == "__main__":
    main()
