#!/usr/bin/env python3
"""
URE MVP Data Ingestion Script
Orchestrates all data ingestion tasks for the MVP
"""

import sys
import os
import logging
import argparse
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.s3_uploader import S3Uploader
from utils.dynamodb_loader import DynamoDBLoader
from utils.bedrock_kb_loader import BedrockKBLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_s3_data(args):
    """Ingest data to S3"""
    logger.info("=" * 60)
    logger.info("STEP 1: S3 DATA INGESTION")
    logger.info("=" * 60)
    
    uploader = S3Uploader(bucket_name=args.s3_bucket, region=args.region)
    
    # Create bucket
    uploader.create_bucket_if_not_exists()
    uploader.enable_versioning()
    
    # Upload PlantVillage dataset
    if args.plantvillage_dir:
        logger.info("\nUploading PlantVillage dataset...")
        stats = uploader.upload_plantvillage_dataset(args.plantvillage_dir)
        logger.info(f"PlantVillage upload: {stats}")
    
    # Upload scheme PDFs
    if args.schemes_dir:
        logger.info("\nUploading scheme PDFs...")
        stats = uploader.upload_scheme_pdfs(args.schemes_dir)
        logger.info(f"Scheme PDFs upload: {stats}")
    
    # Upload Agmarknet data
    if args.agmarknet_csv:
        logger.info("\nUploading Agmarknet data...")
        success = uploader.upload_agmarknet_data(args.agmarknet_csv)
        logger.info(f"Agmarknet upload: {'Success' if success else 'Failed'}")
    
    logger.info("\n✓ S3 data ingestion complete\n")


def ingest_dynamodb_data(args):
    """Ingest data to DynamoDB"""
    logger.info("=" * 60)
    logger.info("STEP 2: DYNAMODB DATA INGESTION")
    logger.info("=" * 60)
    
    loader = DynamoDBLoader(region=args.region)
    
    # Create tables
    logger.info("\nCreating DynamoDB tables...")
    loader.create_conversations_table()
    loader.create_village_amenities_table()
    loader.create_user_profiles_table()
    
    # Load village amenities
    if args.village_csv:
        logger.info("\nLoading village amenities from CSV...")
        stats = loader.load_village_amenities_from_csv(args.village_csv)
        logger.info(f"Village amenities load: {stats}")
    else:
        logger.info("\nLoading sample village data...")
        loader.load_sample_village_data()
    
    # Load sample user profile
    logger.info("\nLoading sample user profile...")
    loader.load_sample_user_profile()
    
    logger.info("\n✓ DynamoDB data ingestion complete\n")


def ingest_bedrock_kb_data(args):
    """Ingest data to Bedrock Knowledge Base"""
    logger.info("=" * 60)
    logger.info("STEP 3: BEDROCK KNOWLEDGE BASE SETUP")
    logger.info("=" * 60)
    
    loader = BedrockKBLoader(region=args.bedrock_region)
    
    # Create OpenSearch collection
    logger.info("\nCreating OpenSearch Serverless collection...")
    collection_arn = loader.create_opensearch_collection()
    
    if not collection_arn:
        logger.error("Failed to create OpenSearch collection")
        return
    
    # Extract collection ID and endpoint from ARN
    collection_id = collection_arn.split('/')[-1]
    collection_endpoint = f'{collection_id}.{args.bedrock_region}.aoss.amazonaws.com'
    
    logger.info(f"Collection endpoint: {collection_endpoint}")
    
    # Create IAM role and policies first
    logger.info("\nCreating IAM role and policies...")
    bedrock_kb_execution_role = loader.create_bedrock_execution_role(
        bucket_name=args.s3_bucket,
        collection_arn=collection_arn
    )
    
    # Create OpenSearch security policies with Bedrock role
    logger.info("\nCreating OpenSearch security policies...")
    loader.create_policies_in_oss(
        collection_name='ure-knowledge-base',
        bedrock_role_arn=bedrock_kb_execution_role['Role']['Arn']
    )
    
    # Wait for policies to propagate
    logger.info("\nWaiting for security policies to propagate...")
    time.sleep(10)
    
    # Create vector index
    logger.info("\nCreating vector index in OpenSearch...")
    loader.create_vector_index(
        collection_endpoint=collection_endpoint,
        index_name='ure-kb-index',
        embedding_dimension=1024  # titan-embed-text-v2:0 uses 1024 dimensions
    )
    
    # Create Knowledge Base
    logger.info("\nCreating Bedrock Knowledge Base...")
    kb_id = loader.create_knowledge_base(
        s3_bucket=args.s3_bucket,
        s3_prefix='schemes/',
        opensearch_collection_arn=collection_arn
    )
    
    if not kb_id:
        logger.error("Failed to create Knowledge Base")
        return
    
    # Create data source
    logger.info("\nCreating data source...")
    data_source_id = loader.create_data_source(
        kb_id=kb_id,
        s3_bucket=args.s3_bucket,
        s3_prefix='schemes/'
    )
    
    if not data_source_id:
        logger.error("Failed to create data source")
        return
    
    # Start ingestion job
    logger.info("\nStarting ingestion job...")
    job_id = loader.start_ingestion_job(kb_id, data_source_id)
    
    if job_id:
        logger.info(f"\n✓ Bedrock KB setup complete")
        logger.info(f"Knowledge Base ID: {kb_id}")
        logger.info(f"Save this ID to .env file: BEDROCK_KB_ID={kb_id}\n")
    else:
        logger.error("Failed to start ingestion job")


def main():
    parser = argparse.ArgumentParser(
        description='URE MVP Data Ingestion Script'
    )
    
    # General arguments
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region for S3 and DynamoDB (default: us-east-1)'
    )
    parser.add_argument(
        '--bedrock-region',
        default='us-east-1',
        help='AWS region for Bedrock (default: us-east-1)'
    )
    parser.add_argument(
        '--s3-bucket',
        default='ure-mvp-data-us-east-1-188238313375',
        help='S3 bucket name (default: ure-mvp-data-us-east-1-188238313375)'
    )
    
    # Data source arguments
    parser.add_argument(
        '--plantvillage-dir',
        help='Path to PlantVillage dataset directory'
    )
    parser.add_argument(
        '--schemes-dir',
        help='Path to government scheme PDFs directory'
    )
    parser.add_argument(
        '--agmarknet-csv',
        help='Path to Agmarknet CSV file'
    )
    parser.add_argument(
        '--village-csv',
        help='Path to village amenities CSV file'
    )
    
    # Step selection
    parser.add_argument(
        '--steps',
        nargs='+',
        choices=['s3', 'dynamodb', 'bedrock', 'all'],
        default=['all'],
        help='Steps to execute (default: all)'
    )
    
    # Sample data flag
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Load sample data for testing (no external datasets required)'
    )
    
    args = parser.parse_args()
    
    # Print configuration
    logger.info("\n" + "=" * 60)
    logger.info("URE MVP DATA INGESTION")
    logger.info("=" * 60)
    logger.info(f"Region: {args.region}")
    logger.info(f"Bedrock Region: {args.bedrock_region}")
    logger.info(f"S3 Bucket: {args.s3_bucket}")
    logger.info(f"Steps: {args.steps}")
    logger.info("=" * 60 + "\n")
    
    # Execute steps
    steps = args.steps if 'all' not in args.steps else ['s3', 'dynamodb', 'bedrock']
    
    try:
        if 's3' in steps:
            if args.sample_data:
                logger.info("Skipping S3 ingestion (sample data mode)")
            else:
                ingest_s3_data(args)
        
        if 'dynamodb' in steps:
            ingest_dynamodb_data(args)
        
        if 'bedrock' in steps:
            if args.sample_data:
                logger.info("Skipping Bedrock KB setup (sample data mode)")
            else:
                ingest_bedrock_kb_data(args)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ DATA INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Update .env file with BEDROCK_KB_ID")
        logger.info("2. Configure MCP servers")
        logger.info("3. Test agents with: python test_agents.py")
        logger.info("=" * 60 + "\n")
    
    except Exception as e:
        logger.error(f"\n✗ Data ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
