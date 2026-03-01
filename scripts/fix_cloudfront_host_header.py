#!/usr/bin/env python3
"""
Fix CloudFront to send correct Host header to App Runner
"""

import boto3
import json

cloudfront = boto3.client('cloudfront', region_name='us-east-1')

DISTRIBUTION_ID = 'E2NAZO9W1Y9K7Y'
APP_RUNNER_DOMAIN = 'pjytmwphqs.us-east-1.awsapprunner.com'

print("\n" + "=" * 60)
print("Fixing CloudFront Host Header")
print("=" * 60)

# Get current configuration
print("\nGetting current configuration...")
response = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
config = response['DistributionConfig']
etag = response['ETag']

# Add custom origin header to preserve the original host
print(f"\nAdding custom origin header: Host = {APP_RUNNER_DOMAIN}")

config['Origins']['Items'][0]['CustomHeaders'] = {
    'Quantity': 1,
    'Items': [
        {
            'HeaderName': 'X-Forwarded-Host',
            'HeaderValue': APP_RUNNER_DOMAIN
        }
    ]
}

# Remove Host from forwarded headers since we're setting it via custom header
forwarded_headers = config['DefaultCacheBehavior']['ForwardedValues']['Headers']['Items']
if 'Host' in forwarded_headers:
    forwarded_headers.remove('Host')
    config['DefaultCacheBehavior']['ForwardedValues']['Headers']['Quantity'] = len(forwarded_headers)

print("✓ Configuration updated")

# Apply changes
print("\nApplying changes...")
try:
    response = cloudfront.update_distribution(
        Id=DISTRIBUTION_ID,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print("✓ Configuration updated successfully!")
    print(f"\nStatus: {response['Distribution']['Status']}")
    print("\n⏳ Wait 5-10 minutes for deployment...")
    print("\nThen test: https://d3klok1uqm8enn.cloudfront.net")
    
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
