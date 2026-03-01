#!/usr/bin/env python3
"""
Check CloudFront distribution deployment status
"""

import boto3
import json
import time
import sys

cloudfront = boto3.client('cloudfront', region_name='us-east-1')

# Load distribution info
try:
    with open('cloudfront_distribution.json', 'r') as f:
        dist_info = json.load(f)
        distribution_id = dist_info['distribution_id']
        domain_name = dist_info['domain_name']
except FileNotFoundError:
    print("✗ cloudfront_distribution.json not found")
    print("Run setup_cloudfront_cdn.py first")
    sys.exit(1)

print("\n" + "=" * 60)
print("CloudFront Distribution Status")
print("=" * 60)
print(f"\nDistribution ID: {distribution_id}")
print(f"Domain Name: {domain_name}\n")

try:
    response = cloudfront.get_distribution(Id=distribution_id)
    
    status = response['Distribution']['Status']
    enabled = response['Distribution']['DistributionConfig']['Enabled']
    
    print(f"Status: {status}")
    print(f"Enabled: {enabled}")
    
    if status == 'Deployed':
        print("\n✓ CloudFront distribution is DEPLOYED and ready!")
        print("\n" + "=" * 60)
        print("ACCESS YOUR APP")
        print("=" * 60)
        print(f"\nCloudFront URL (FAST - Global CDN):")
        print(f"  https://{domain_name}")
        print(f"\nDirect App Runner URL (Slower):")
        print(f"  https://{dist_info['origin']}")
        print("\n" + "=" * 60)
        print("\nRECOMMENDATION:")
        print("Use the CloudFront URL for production!")
        print("It provides:")
        print("  - Faster loading times globally")
        print("  - Edge caching for static assets")
        print("  - DDoS protection")
        print("  - Lower latency worldwide")
        print("\n" + "=" * 60)
    
    elif status == 'InProgress':
        print("\n⏳ Distribution is still deploying...")
        print("This typically takes 10-15 minutes.")
        print("\nWaiting for deployment to complete...")
        
        max_attempts = 60
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(15)
            attempt += 1
            
            response = cloudfront.get_distribution(Id=distribution_id)
            status = response['Distribution']['Status']
            
            print(f"  Attempt {attempt}/{max_attempts} - Status: {status}")
            
            if status == 'Deployed':
                print("\n✓ CloudFront distribution is DEPLOYED!")
                print(f"\nAccess your app at: https://{domain_name}")
                break
        
        if attempt >= max_attempts:
            print("\n⚠ Deployment is taking longer than expected.")
            print("Check AWS Console for details:")
            print("  https://console.aws.amazon.com/cloudfront/v3/home")
    
    else:
        print(f"\n⚠ Unexpected status: {status}")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
