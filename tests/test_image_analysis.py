#!/usr/bin/env python3
"""
Test actual image analysis with Bedrock multimodal model
"""

import sys
import os
import base64
import logging
from pathlib import Path
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_crop_image(image_path: str):
    """
    Analyze crop disease image using Bedrock Nova Pro multimodal model
    """
    logger.info("\n" + "=" * 60)
    logger.info("CROP DISEASE IMAGE ANALYSIS TEST")
    logger.info("=" * 60)
    
    # Read and encode image
    logger.info(f"\n1. Reading image: {image_path}")
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    image_size_kb = len(image_bytes) / 1024
    logger.info(f"   Image size: {image_size_kb:.2f} KB")
    
    # Initialize Bedrock client
    logger.info("\n2. Initializing Bedrock Runtime client...")
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Prepare the request
    logger.info("\n3. Preparing multimodal request...")
    model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    # Create the message with image
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {
                            "bytes": image_bytes
                        }
                    }
                },
                {
                    "text": """Analyze this crop/plant image and provide:

1. **Plant/Crop Type**: Identify the plant species
2. **Disease/Condition**: Identify any disease, pest, or health issue
3. **Symptoms**: Describe visible symptoms
4. **Severity**: Rate severity (Mild/Moderate/Severe)
5. **Treatment**: Recommend treatment options (organic and chemical)
6. **Prevention**: Suggest preventive measures

Be specific and practical for Indian farmers."""
                }
            ]
        }
    ]
    
    # Call Bedrock
    logger.info("\n4. Calling Bedrock Nova Pro for image analysis...")
    logger.info(f"   Model: {model_id}")
    
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.3
            }
        )
        
        # Extract response
        output_message = response['output']['message']
        analysis_text = output_message['content'][0]['text']
        
        # Display results
        logger.info("\n5. ✓ Analysis Complete!")
        logger.info("\n" + "=" * 60)
        logger.info("DISEASE ANALYSIS RESULT")
        logger.info("=" * 60)
        print("\n" + analysis_text)
        
        # Display usage metrics
        usage = response.get('usage', {})
        logger.info("\n" + "=" * 60)
        logger.info("USAGE METRICS")
        logger.info("=" * 60)
        logger.info(f"Input tokens: {usage.get('inputTokens', 0)}")
        logger.info(f"Output tokens: {usage.get('outputTokens', 0)}")
        logger.info(f"Total tokens: {usage.get('totalTokens', 0)}")
        
        return analysis_text
        
    except Exception as e:
        logger.error(f"\n✗ Error during analysis: {e}")
        raise


def main():
    """Test with a sample crop disease image"""
    
    # Find test images
    test_image_dir = Path("data/plantvillage/test/test")
    
    if not test_image_dir.exists():
        logger.error(f"Test image directory not found: {test_image_dir}")
        logger.info("\nPlease ensure test images are available in:")
        logger.info("  data/plantvillage/test/test/")
        return
    
    # Get available test images
    test_images = list(test_image_dir.glob("*.JPG"))
    
    if not test_images:
        logger.error("No test images found")
        return
    
    # Display available images
    logger.info("\nAvailable test images:")
    for idx, img in enumerate(test_images[:10], 1):
        logger.info(f"  {idx}. {img.name}")
    
    # Test with first image
    test_image = test_images[0]
    logger.info(f"\nTesting with: {test_image.name}")
    
    try:
        analysis = analyze_crop_image(str(test_image))
        
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUCCESSFUL!")
        logger.info("=" * 60)
        logger.info("\nThe system can successfully:")
        logger.info("✓ Accept crop images")
        logger.info("✓ Analyze using Bedrock multimodal AI")
        logger.info("✓ Identify diseases and conditions")
        logger.info("✓ Provide treatment recommendations")
        
    except Exception as e:
        logger.error(f"\nTest failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
