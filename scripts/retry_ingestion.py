#!/usr/bin/env python3
"""
Retry Bedrock Knowledge Base Ingestion
"""

import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.bedrock_kb_loader import BedrockKBLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    kb_id = '7XROZ6PZIF'
    s3_bucket = 'ure-mvp-data-us-east-1-188238313375'
    s3_prefix = 'schemes/'
    
    logger.info("=" * 60)
    logger.info("BEDROCK KB INGESTION RETRY - US-EAST-1 BUCKET")
    logger.info("=" * 60)
    
    # Initialize loader
    loader = BedrockKBLoader(region='us-east-1')
    
    # Step 1: Create new data source with us-east-1 bucket
    logger.info(f"\nStep 1: Creating data source for KB: {kb_id}")
    logger.info(f"Bucket: {s3_bucket} (us-east-1)")
    data_source_id = loader.create_data_source(
        kb_id=kb_id,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix
    )
    
    if not data_source_id:
        logger.error("Failed to create data source")
        return
    
    logger.info(f"✓ Data source created: {data_source_id}")
    
    # Step 2: Start ingestion job
    logger.info(f"\nStep 2: Starting ingestion job...")
    job_id = loader.start_ingestion_job(kb_id, data_source_id)
    
    if job_id:
        logger.info(f"\n✓ Ingestion job started successfully")
        logger.info(f"Job ID: {job_id}")
        logger.info("\nMonitoring ingestion job status...")
    else:
        logger.error("Failed to start ingestion job")


if __name__ == "__main__":
    main()
