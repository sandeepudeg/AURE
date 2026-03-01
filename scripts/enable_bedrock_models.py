#!/usr/bin/env python3
"""
Enable Bedrock Model Access
Automates enabling model access for required Bedrock models
"""

import boto3
import logging
import time
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enable_model_access(region='us-east-1'):
    """
    Enable access to required Bedrock models
    
    Note: Model access requests are typically approved automatically for most models.
    Some models may require use case submission which cannot be automated.
    """
    bedrock = boto3.client('bedrock', region_name=region)
    
    # Models we need for URE
    required_models = [
        'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'amazon.titan-embed-text-v2:0',
        'anthropic.claude-3-5-sonnet-20241022-v2:0'
    ]
    
    logger.info("=" * 60)
    logger.info("BEDROCK MODEL ACCESS ENABLEMENT")
    logger.info("=" * 60)
    
    # Check current model access
    logger.info("\nChecking current model access...")
    try:
        response = bedrock.list_foundation_models()
        available_models = {model['modelId']: model for model in response.get('modelSummaries', [])}
        
        logger.info(f"Found {len(available_models)} available models in {region}")
        
        # Check which models we need
        for model_id in required_models:
            if model_id in available_models:
                model_info = available_models[model_id]
                logger.info(f"\n✓ Model available: {model_id}")
                logger.info(f"  Provider: {model_info.get('providerName')}")
                logger.info(f"  Status: {model_info.get('modelLifecycle', {}).get('status', 'UNKNOWN')}")
            else:
                logger.warning(f"\n✗ Model not found: {model_id}")
        
        # Try to get model invocation logging configuration
        logger.info("\n" + "=" * 60)
        logger.info("Checking model invocation logging...")
        try:
            logging_config = bedrock.get_model_invocation_logging_configuration()
            logger.info(f"Logging configuration: {logging_config.get('loggingConfig', {})}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info("Model invocation logging not configured")
            else:
                logger.warning(f"Could not check logging configuration: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("MODEL ACCESS CHECK COMPLETE")
        logger.info("=" * 60)
        
        logger.info("\nNOTE: If models show as unavailable:")
        logger.info("1. Go to AWS Bedrock Console")
        logger.info("2. Navigate to 'Model access' in the left sidebar")
        logger.info("3. Click 'Manage model access'")
        logger.info("4. Enable the required models:")
        for model_id in required_models:
            logger.info(f"   - {model_id}")
        logger.info("5. Submit the request (usually approved instantly)")
        
    except ClientError as e:
        logger.error(f"Failed to check model access: {e}")
        return False
    
    return True


def test_model_invocation(region='us-east-1'):
    """Test if we can invoke a model"""
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
    
    logger.info("\n" + "=" * 60)
    logger.info("TESTING MODEL INVOCATION")
    logger.info("=" * 60)
    
    # Try Claude 3.5 Sonnet
    model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    logger.info(f"\nTesting model: {model_id}")
    
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Say hello in one word"}]
                }
            ]
        )
        
        output_text = response['output']['message']['content'][0]['text']
        logger.info(f"✓ Model invocation successful!")
        logger.info(f"Response: {output_text}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if 'ResourceNotFoundException' in error_code:
            logger.error(f"✗ Model access not enabled: {error_message}")
            logger.info("\nTo enable model access:")
            logger.info("Run: py scripts/enable_bedrock_models.py")
        elif 'AccessDeniedException' in error_code:
            logger.error(f"✗ Access denied: {error_message}")
        else:
            logger.error(f"✗ Error: {error_code} - {error_message}")
        
        return False


def main():
    """Main function"""
    region = 'us-east-1'
    
    # Check model access
    enable_model_access(region)
    
    # Test model invocation
    test_model_invocation(region)


if __name__ == "__main__":
    main()
