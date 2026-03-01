#!/usr/bin/env python3
"""
List all available Bedrock models and their status
"""

import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bedrock = boto3.client('bedrock', region_name='us-east-1')

response = bedrock.list_foundation_models()

logger.info("\n" + "=" * 80)
logger.info("AVAILABLE BEDROCK MODELS")
logger.info("=" * 80)

# Filter for active models we can use
active_models = []
for model in response['modelSummaries']:
    status = model.get('modelLifecycle', {}).get('status', 'UNKNOWN')
    provider = model.get('providerName', 'Unknown')
    model_id = model['modelId']
    
    # Look for Claude, Nova, and Titan models that are ACTIVE
    if status == 'ACTIVE' and any(x in model_id.lower() for x in ['claude', 'nova', 'titan']):
        active_models.append(model)
        logger.info(f"\n✓ {model_id}")
        logger.info(f"  Provider: {provider}")
        logger.info(f"  Status: {status}")
        logger.info(f"  Input modalities: {model.get('inputModalities', [])}")
        logger.info(f"  Output modalities: {model.get('outputModalities', [])}")

logger.info(f"\n\nFound {len(active_models)} active models")
