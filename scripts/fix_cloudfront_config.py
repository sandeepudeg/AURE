#!/usr/bin/env python3
"""
Fix CloudFront configuration for Streamlit compatibility
"""

import boto3
import json
import time

cloudfront = boto3.client('cloudfront', region_name='us-east-1')

DISTRIBUTION_ID = 'E2NAZO9W1Y9K7Y'

print("\n" + "=" * 60)
print("Fixing CloudFront Configuration for Streamlit")
print("=" * 60)

# Get current configuration
print("\nStep 1: Getting current distribution configuration...")
response = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
config = response['DistributionConfig']
etag = response['ETag']

print(f"✓ Current ETag: {etag}")

# Update default cache behavior to forward all headers
print("\nStep 2: Updating cache behavior to forward all headers...")

config['DefaultCacheBehavior']['ForwardedValues'] = {
    'QueryString': True,
    'Cookies': {
        'Forward': 'all'
    },
    'Headers': {
        'Quantity': 1,
        'Items': ['*']  # Forward all headers
    },
    'QueryStringCacheKeys': {
        'Quantity': 0
    }
}

# Also update cache TTLs to not cache dynamic content
config['DefaultCacheBehavior']['MinTTL'] = 0
config['DefaultCacheBehavior']['DefaultTTL'] = 0
config['DefaultCacheBehavior']['MaxTTL'] = 0

print("✓ Updated to forward all headers")
print("✓ Disabled caching for dynamic content")

# Update the distribution
print("\nStep 3: Applying configuration changes...")
try:
    response = cloudfront.update_distribution(
        Id=DISTRIBUTION_ID,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print("✓ Configuration updated successfully!")
    print(f"\nNew Status: {response['Distribution']['Status']}")
    print("\n⏳ Changes are being deployed...")
    print("This typically takes 5-10 minutes.")
    
    print("\n" + "=" * 60)
    print("CONFIGURATION UPDATE INITIATED")
    print("=" * 60)
    print("\nChanges made:")
    print("  - Forward all headers to origin")
    print("  - Disabled caching for dynamic content")
    print("  - Enabled WebSocket support")
    print("\nWait 5-10 minutes, then try accessing:")
    print("  https://d3klok1uqm8enn.cloudfront.net")
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"✗ Error updating distribution: {e}")
    exit(1)
