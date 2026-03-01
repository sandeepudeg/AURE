#!/usr/bin/env python3
"""
Copy PlantVillage dataset to us-east-1 bucket
"""

import sys
import os
import logging
import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def copy_plantvillage_images(source_bucket: str, dest_bucket: str, prefix: str = 'plantvillage/'):
    """Copy PlantVillage images from source to destination bucket"""
    s3_source = boto3.client('s3', region_name='ap-south-1')
    s3_dest = boto3.client('s3', region_name='us-east-1')
    
    logger.info(f"Copying PlantVillage images from {source_bucket} to {dest_bucket}")
    logger.info("This will take several minutes due to the large number of files...")
    
    # List all objects with pagination
    paginator = s3_source.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=source_bucket, Prefix=prefix)
    
    # Count total objects first
    logger.info("Counting total files...")
    total_count = 0
    for page in pages:
        if 'Contents' in page:
            total_count += len([obj for obj in page['Contents'] if not obj['Key'].endswith('/')])
    
    logger.info(f"Found {total_count} files to copy")
    
    # Copy objects with progress bar
    pages = paginator.paginate(Bucket=source_bucket, Prefix=prefix)
    copied_count = 0
    
    with tqdm(total=total_count, desc="Copying images", unit="file") as pbar:
        for page in pages:
            if 'Contents' not in page:
                continue
            
            for obj in page['Contents']:
                key = obj['Key']
                
                # Skip directory markers
                if key.endswith('/'):
                    continue
                
                # Copy object
                copy_source = {'Bucket': source_bucket, 'Key': key}
                s3_dest.copy_object(
                    CopySource=copy_source,
                    Bucket=dest_bucket,
                    Key=key
                )
                copied_count += 1
                pbar.update(1)
    
    logger.info(f"✓ Copied {copied_count} files")
    return copied_count


def main():
    account_id = '188238313375'
    source_bucket = f'ure-mvp-data-{account_id}'
    dest_bucket = f'ure-mvp-data-us-east-1-{account_id}'
    
    logger.info("=" * 60)
    logger.info("COPY PLANTVILLAGE DATASET TO US-EAST-1")
    logger.info("=" * 60)
    
    # Copy PlantVillage images
    logger.info("\nCopying PlantVillage dataset...")
    copied = copy_plantvillage_images(source_bucket, dest_bucket, 'plantvillage/')
    
    logger.info(f"\n{'=' * 60}")
    logger.info("SUCCESS!")
    logger.info(f"{'=' * 60}")
    logger.info(f"Copied {copied} images to {dest_bucket}")


if __name__ == "__main__":
    main()
