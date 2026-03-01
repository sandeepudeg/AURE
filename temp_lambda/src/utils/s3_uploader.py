#!/usr/bin/env python3
"""
S3 Uploader Utility for URE MVP
-------------------------------
This script handles the migration of local datasets (Images, CSVs, PDFs) 
from a Windows machine to AWS S3. It includes a real-time progress bar 
system using 'tqdm' to monitor large file uploads (like the 2GB PlantVillage set).
"""

import os
import boto3
import logging
from pathlib import Path
from typing import Optional, List
from botocore.exceptions import ClientError
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ProgressPercentage(object):
    """
    Callback class for boto3 to update tqdm progress bar.
    
    Boto3's upload_file method accepts a 'Callback' parameter that 
    periodically sends the number of bytes transferred.
    """
    def __init__(self, filename):
        self._filename = os.path.basename(filename)
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        # Initialize the progress bar with file size in Bytes (unit='B')
        self._pbar = tqdm(
            total=self._size, 
            unit='B', 
            unit_scale=True, 
            desc=f"Uploading {self._filename[:20]}...", # Truncate long names for UI
            leave=False # Bar disappears on completion to avoid terminal clutter
        )

    def __call__(self, bytes_amount):
        """Called by boto3 every time a chunk of bytes is uploaded."""
        self._seen_so_far += bytes_amount
        self._pbar.update(bytes_amount)
        if self._seen_so_far >= self._size:
            self._pbar.close()

class S3Uploader:
    """Manages S3 bucket operations and dataset ingestion for the URE system."""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        """
        Args:
            bucket_name: The target S3 bucket (e.g., 'knowledge-base-bharat').
            region: Defaults to us-east-1 for Bedrock compatibility.
        """
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
        
        logger.info(f"S3 Uploader initialized for bucket: {bucket_name}")
    
    def create_bucket_if_not_exists(self):
        """Checks for bucket existence; creates it if missing with regional config."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creating bucket: {self.bucket_name}")
                # us-east-1 does not require LocationConstraint
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                logger.info(f"Bucket {self.bucket_name} created successfully")
            else:
                raise
    
    def enable_versioning(self):
        """Enables versioning to protect against accidental data deletion."""
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            logger.info(f"Versioning enabled for bucket: {self.bucket_name}")
        except ClientError as e:
            logger.error(f"Failed to enable versioning: {e}")
            raise
    
    def upload_file(
        self,
        local_path: str,
        s3_key: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Uploads a single file and displays a progress bar.
        
        Args:
            local_path: Path on your D: drive.
            s3_key: Path inside the S3 bucket.
            metadata: Custom key-value pairs for S3 object indexing.
        """
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Attach the progress callback class
            progress_callback = ProgressPercentage(local_path)
            
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
                Callback=progress_callback
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def upload_directory(
        self,
        local_dir: str,
        s3_prefix: str,
        file_extensions: Optional[List[str]] = None
    ) -> dict:
        """
        Recursively walks through a local folder and uploads matching files.
        """
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        local_path = Path(local_dir)
        
        if not local_path.exists():
            logger.error(f"Directory not found: {local_dir}")
            return stats
        
        # Gather list of all files first
        all_files = [f for f in local_path.rglob('*') if f.is_file()]
        
        logger.info(f"Scanning {len(all_files)} files in {local_dir}...")
        for file_path in all_files:
            # Skip files if they don't match the requested extensions (.pdf, .jpg, etc)
            if file_extensions and file_path.suffix.lower() not in file_extensions:
                stats['skipped'] += 1
                continue
            
            # Convert Windows backslashes (\) to S3 forward slashes (/)
            relative_path = file_path.relative_to(local_path)
            s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/')
            
            if self.upload_file(str(file_path), s3_key):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        logger.info(f"Upload Batch Complete: {stats}")
        return stats
    
    def upload_plantvillage_dataset(self, local_dir: str) -> dict:
        """Specific wrapper for the Crop Disease image dataset."""
        logger.info("Starting PlantVillage image sync (Multimodal Data)...")
        return self.upload_directory(
            local_dir=local_dir,
            s3_prefix='plantvillage',
            file_extensions=['.jpg', '.jpeg', '.png']
        )
    
    def upload_scheme_pdfs(self, local_dir: str) -> dict:
        """Specific wrapper for government PDFs to be used by Bedrock RAG."""
        logger.info("Starting Scheme PDF sync (Knowledge Base Data)...")
        return self.upload_directory(
            local_dir=local_dir,
            s3_prefix='schemes',
            file_extensions=['.pdf', '.doc', '.docx']
        )
    
    def upload_agmarknet_data(self, csv_path: str) -> bool:
        """Uploads the Mandi pricing CSV with specific metadata for the Market Agent."""
        logger.info("Uploading Agmarknet Price CSV...")
        return self.upload_file(
            local_path=csv_path,
            s3_key='datasets/agmarknet_prices.csv',
            metadata={'source': 'agmarknet', 'category': 'market_intelligence'}
        )

if __name__ == "__main__":
    # Basic configuration for standalone testing
    logging.basicConfig(level=logging.INFO)
    # Initialize uploader
    uploader = S3Uploader(bucket_name='knowledge-base-bharat')
    # Create bucket    
    uploader.create_bucket_if_not_exists()
    uploader.enable_versioning()
    print("\nS3 Uploader ready!")
    print("Use the following methods:")
    print("  - upload_plantvillage_dataset(local_dir)")
    print("  - upload_scheme_pdfs(local_dir)")
    print("  - upload_agmarknet_data(csv_path)")
    print("\nS3 Uploader Utility Ready for URE Ingestion.")
    