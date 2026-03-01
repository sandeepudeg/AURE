#!/usr/bin/env python3
"""
Deploy simple web UI to S3 with CloudFront CDN
"""

import boto3
import json
import time
from pathlib import Path

# Configuration
REGION = 'ap-south-1'
BUCKET_NAME = 'ure-web-ui-mumbai'
CLOUDFRONT_COMMENT = 'URE Web UI Distribution'

def create_s3_bucket():
    """Create S3 bucket for static website hosting"""
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        # Create bucket
        if REGION == 'us-east-1':
            s3.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        print(f"✓ Created S3 bucket: {BUCKET_NAME}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"✓ S3 bucket already exists: {BUCKET_NAME}")
    except Exception as e:
        print(f"✗ Error creating bucket: {e}")
        raise
    
    # Configure bucket for static website hosting
    s3.put_bucket_website(
        Bucket=BUCKET_NAME,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'index.html'}
        }
    )
    print("✓ Configured static website hosting")
    
    # Set bucket policy for public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }
    
    s3.put_bucket_policy(
        Bucket=BUCKET_NAME,
        Policy=json.dumps(bucket_policy)
    )
    print("✓ Set bucket policy for public access")
    
    # Disable block public access
    s3.put_public_access_block(
        Bucket=BUCKET_NAME,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )
    print("✓ Disabled block public access")

def upload_files():
    """Upload web files to S3"""
    s3 = boto3.client('s3', region_name=REGION)
    
    files = [
        ('src/web/complete.html', 'index.html', 'text/html'),
        ('src/web/complete.css', 'complete.css', 'text/css'),
        ('src/web/complete.js', 'complete.js', 'application/javascript')
    ]
    
    for local_path, s3_key, content_type in files:
        with open(local_path, 'rb') as f:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=f,
                ContentType=content_type,
                CacheControl='max-age=300'  # 5 minutes cache
            )
        print(f"✓ Uploaded {local_path} -> s3://{BUCKET_NAME}/{s3_key}")

def create_cloudfront_distribution():
    """Create CloudFront distribution for global CDN"""
    cloudfront = boto3.client('cloudfront')
    
    # Get S3 website endpoint
    website_endpoint = f"{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"
    
    distribution_config = {
        'CallerReference': str(time.time()),
        'Comment': CLOUDFRONT_COMMENT,
        'Enabled': True,
        'DefaultRootObject': 'index.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'S3-Website',
                    'DomainName': website_endpoint,
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only'
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3-Website',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD']
                }
            },
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0,
            'DefaultTTL': 300,
            'MaxTTL': 86400,
            'Compress': True
        },
        'CustomErrorResponses': {
            'Quantity': 1,
            'Items': [
                {
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 300
                }
            ]
        },
        'PriceClass': 'PriceClass_All'
    }
    
    try:
        response = cloudfront.create_distribution(
            DistributionConfig=distribution_config
        )
        
        distribution_id = response['Distribution']['Id']
        domain_name = response['Distribution']['DomainName']
        
        print(f"✓ Created CloudFront distribution: {distribution_id}")
        print(f"✓ CloudFront domain: https://{domain_name}")
        print("\n⏳ Distribution is deploying (takes 5-10 minutes)...")
        
        return distribution_id, domain_name
        
    except Exception as e:
        print(f"✗ Error creating CloudFront distribution: {e}")
        raise

def main():
    print("=" * 60)
    print("URE Web UI Deployment")
    print("=" * 60)
    
    print("\n[1/3] Creating S3 bucket...")
    create_s3_bucket()
    
    print("\n[2/3] Uploading files...")
    upload_files()
    
    print("\n[3/3] Creating CloudFront distribution...")
    distribution_id, domain_name = create_cloudfront_distribution()
    
    # Get S3 website URL
    s3_url = f"http://{BUCKET_NAME}.s3-website.{REGION}.amazonaws.com"
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE")
    print("=" * 60)
    print(f"\nS3 Website URL (direct):")
    print(f"  {s3_url}")
    print(f"\nCloudFront URL (CDN, use this for production):")
    print(f"  https://{domain_name}")
    print(f"\nDistribution ID: {distribution_id}")
    print("\nNote: CloudFront distribution takes 5-10 minutes to deploy.")
    print("      The S3 URL works immediately for testing.")
    print("\nAPI Endpoint: https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query")
    print("=" * 60)

if __name__ == '__main__':
    main()
