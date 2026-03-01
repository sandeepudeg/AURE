#!/usr/bin/env python3
"""
List Bedrock inference profiles
"""

import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bedrock = boto3.client('bedrock', region_name='us-east-1')

try:
    response = bedrock.list_inference_profiles()
    
    logger.info("\n" + "=" * 80)
    logger.info("AVAILABLE INFERENCE PROFILES")
    logger.info("=" * 80)
    
    for profile in response.get('inferenceProfileSummaries', []):
        profile_id = profile.get('inferenceProfileId')
        profile_arn = profile.get('inferenceProfileArn')
        models = profile.get('models', [])
        
        # Look for Nova Pro profiles
        if 'nova-pro' in profile_id.lower():
            logger.info(f"\n✓ {profile_id}")
            logger.info(f"  ARN: {profile_arn}")
            logger.info(f"  Models: {models}")
            logger.info(f"  Status: {profile.get('status')}")
            logger.info(f"  Type: {profile.get('type')}")
    
except Exception as e:
    logger.error(f"Error: {e}")
