#!/usr/bin/env python3
"""
Setup CloudFront CDN for Streamlit App Runner
"""

import boto3
import json
import time
import sys

# Configuration
AWS_REGION = "us-east-1"
APP_RUNNER_URL = "pjytmwphqs.us-east-1.awsapprunner.com"
DISTRIBUTION_COMMENT = "URE Streamlit UI CDN"

cloudfront = boto3.client('cloudfront', region_name=AWS_REGION)

print("\n" + "=" * 60)
print("Setting up CloudFront CDN for Streamlit UI")
print("=" * 60)
print(f"\nOrigin: {APP_RUNNER_URL}\n")

# CloudFront distribution configuration
distribution_config = {
    'CallerReference': f'ure-streamlit-{int(time.time())}',
    'Comment': DISTRIBUTION_COMMENT,
    'Enabled': True,
    'Origins': {
        'Quantity': 1,
        'Items': [
            {
                'Id': 'app-runner-origin',
                'DomainName': APP_RUNNER_URL,
                'CustomOriginConfig': {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'https-only',
                    'OriginSslProtocols': {
                        'Quantity': 3,
                        'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2']
                    },
                    'OriginReadTimeout': 60,
                    'OriginKeepaliveTimeout': 5
                }
            }
        ]
    },
    'DefaultCacheBehavior': {
        'TargetOriginId': 'app-runner-origin',
        'ViewerProtocolPolicy': 'redirect-to-https',
        'AllowedMethods': {
            'Quantity': 7,
            'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
            'CachedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD']
            }
        },
        'Compress': True,
        'ForwardedValues': {
            'QueryString': True,
            'Cookies': {
                'Forward': 'all'
            },
            'Headers': {
                'Quantity': 4,
                'Items': [
                    'Host',
                    'CloudFront-Forwarded-Proto',
                    'CloudFront-Is-Desktop-Viewer',
                    'CloudFront-Is-Mobile-Viewer'
                ]
            }
        },
        'MinTTL': 0,
        'DefaultTTL': 0,  # Don't cache dynamic content by default
        'MaxTTL': 31536000,
        'TrustedSigners': {
            'Enabled': False,
            'Quantity': 0
        }
    },
    'CacheBehaviors': {
        'Quantity': 2,
        'Items': [
            {
                # Cache static assets
                'PathPattern': '/static/*',
                'TargetOriginId': 'app-runner-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'Compress': True,
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {
                        'Forward': 'none'
                    }
                },
                'MinTTL': 86400,  # 1 day
                'DefaultTTL': 86400,
                'MaxTTL': 31536000,  # 1 year
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                }
            },
            {
                # Cache Streamlit static files
                'PathPattern': '/_stcore/static/*',
                'TargetOriginId': 'app-runner-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'Compress': True,
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {
                        'Forward': 'none'
                    }
                },
                'MinTTL': 86400,
                'DefaultTTL': 86400,
                'MaxTTL': 31536000,
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                }
            }
        ]
    },
    'PriceClass': 'PriceClass_100',  # Use only North America and Europe edge locations
    'ViewerCertificate': {
        'CloudFrontDefaultCertificate': True,
        'MinimumProtocolVersion': 'TLSv1.2_2021'
    }
}

print("Step 1: Creating CloudFront distribution...")
print("This may take 10-15 minutes to deploy globally...\n")

try:
    response = cloudfront.create_distribution(DistributionConfig=distribution_config)
    
    distribution_id = response['Distribution']['Id']
    distribution_domain = response['Distribution']['DomainName']
    status = response['Distribution']['Status']
    
    print(f"✓ Distribution created!")
    print(f"  Distribution ID: {distribution_id}")
    print(f"  Domain Name: {distribution_domain}")
    print(f"  Status: {status}")
    
    print("\n" + "=" * 60)
    print("CLOUDFRONT CDN SETUP INITIATED")
    print("=" * 60)
    print(f"\nYour CloudFront URL:")
    print(f"  https://{distribution_domain}")
    print(f"\nDistribution ID: {distribution_id}")
    print(f"\nStatus: {status}")
    print("\n⏳ Distribution is being deployed to edge locations worldwide...")
    print("This typically takes 10-15 minutes.")
    print("\nYou can check the status with:")
    print(f"  aws cloudfront get-distribution --id {distribution_id}")
    print("\nOnce status is 'Deployed', access your app via CloudFront URL for faster loading!")
    print("\n" + "=" * 60)
    
    # Save distribution info
    with open('cloudfront_distribution.json', 'w') as f:
        json.dump({
            'distribution_id': distribution_id,
            'domain_name': distribution_domain,
            'origin': APP_RUNNER_URL,
            'status': status
        }, f, indent=2)
    
    print("\n✓ Distribution info saved to cloudfront_distribution.json")
    
except Exception as e:
    print(f"✗ Error creating distribution: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("BENEFITS OF CLOUDFRONT CDN")
print("=" * 60)
print("""
✓ Faster loading times globally (edge locations worldwide)
✓ Reduced latency for users far from us-east-1
✓ Static assets cached at edge locations
✓ HTTPS enabled by default
✓ DDoS protection included
✓ Reduced load on App Runner origin

COST: ~$1-5/month for typical usage (first 1TB free tier)
""")
