#!/usr/bin/env python3
"""
Test image upload and disease detection flow
Demonstrates how farmers will upload crop images
"""

import sys
import os
import base64
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def simulate_web_upload(image_path: str, user_id: str = "farmer_001"):
    """
    Simulate web interface image upload
    This is how the web UI will send images to the backend
    """
    logger.info("\n" + "=" * 60)
    logger.info("SIMULATING WEB INTERFACE IMAGE UPLOAD")
    logger.info("=" * 60)
    
    # Step 1: User selects image from file picker or camera
    logger.info(f"\n1. User selects image: {image_path}")
    
    # Step 2: Frontend converts image to base64
    logger.info("2. Frontend converts image to base64...")
    image_base64 = encode_image_to_base64(image_path)
    logger.info(f"   Image size: {len(image_base64)} characters")
    
    # Step 3: Frontend sends POST request to API Gateway
    logger.info("3. Frontend sends POST request to API Gateway")
    request_payload = {
        "user_id": user_id,
        "query": "What disease is affecting my crop?",
        "image": image_base64,
        "language": "en"
    }
    
    logger.info(f"   Request payload size: {len(json.dumps(request_payload))} bytes")
    
    # Step 4: API Gateway triggers Lambda
    logger.info("4. API Gateway triggers Lambda function")
    logger.info("   Lambda processes image:")
    logger.info("   - Decodes base64")
    logger.info("   - Uploads to S3")
    logger.info("   - Generates S3 URI")
    logger.info("   - Passes to Agri-Expert Agent")
    
    # Step 5: Agent analyzes image
    logger.info("5. Agri-Expert Agent analyzes image with Bedrock")
    logger.info("   - Uses Claude/Nova multimodal model")
    logger.info("   - Identifies disease from visual symptoms")
    logger.info("   - Searches PlantVillage database")
    logger.info("   - Retrieves treatment recommendations")
    
    # Step 6: Response sent back
    logger.info("6. Response sent back to user")
    logger.info("   - Disease name")
    logger.info("   - Confidence score")
    logger.info("   - Treatment recommendations")
    logger.info("   - Preventive measures")
    
    return request_payload


def simulate_whatsapp_upload(image_path: str, phone_number: str = "+91XXXXXXXXXX"):
    """
    Simulate WhatsApp image upload
    This is how WhatsApp bot will receive images
    """
    logger.info("\n" + "=" * 60)
    logger.info("SIMULATING WHATSAPP IMAGE UPLOAD")
    logger.info("=" * 60)
    
    # Step 1: Farmer sends image via WhatsApp
    logger.info(f"\n1. Farmer sends image via WhatsApp from {phone_number}")
    
    # Step 2: Twilio webhook receives image
    logger.info("2. Twilio webhook receives image URL")
    logger.info("   - Twilio provides media URL")
    logger.info("   - Webhook downloads image")
    logger.info("   - Converts to base64")
    
    # Step 3: Same flow as web upload
    logger.info("3. Webhook calls Lambda with base64 image")
    logger.info("   (Same processing as web upload)")
    
    # Step 4: Response sent via WhatsApp
    logger.info("4. Response sent back via WhatsApp message")
    logger.info("   - Text response with disease info")
    logger.info("   - Treatment recommendations")
    logger.info("   - Links to detailed guides")


def simulate_mobile_app_upload(image_path: str, user_id: str = "farmer_001"):
    """
    Simulate mobile app image upload
    This is how mobile app will send images
    """
    logger.info("\n" + "=" * 60)
    logger.info("SIMULATING MOBILE APP IMAGE UPLOAD")
    logger.info("=" * 60)
    
    # Step 1: User captures or selects image
    logger.info(f"\n1. User captures/selects image in mobile app")
    
    # Step 2: App compresses and encodes image
    logger.info("2. App compresses image (to reduce data usage)")
    logger.info("   - Resize to max 1024x1024")
    logger.info("   - Convert to JPEG with 80% quality")
    logger.info("   - Encode to base64")
    
    # Step 3: App sends to API
    logger.info("3. App sends POST request to API")
    logger.info("   (Same payload as web upload)")
    
    # Step 4: Response displayed in app
    logger.info("4. Response displayed in app UI")
    logger.info("   - Disease card with image")
    logger.info("   - Treatment steps")
    logger.info("   - Save to history")


def main():
    """Demonstrate all image upload methods"""
    logger.info("\n" + "=" * 60)
    logger.info("URE IMAGE UPLOAD FLOW DEMONSTRATION")
    logger.info("=" * 60)
    
    # Find a test image
    test_image_dir = Path("data/plantvillage/test/test")
    if test_image_dir.exists():
        test_images = list(test_image_dir.glob("*.JPG"))
        if test_images:
            test_image = str(test_images[0])
            logger.info(f"\nUsing test image: {test_image}")
            
            # Demonstrate all upload methods
            simulate_web_upload(test_image)
            simulate_whatsapp_upload(test_image)
            simulate_mobile_app_upload(test_image)
            
            logger.info("\n" + "=" * 60)
            logger.info("KEY POINTS")
            logger.info("=" * 60)
            logger.info("\n1. All channels use the same backend Lambda function")
            logger.info("2. Images are always base64-encoded in transit")
            logger.info("3. Lambda uploads to S3 for permanent storage")
            logger.info("4. S3 URI is passed to Bedrock for analysis")
            logger.info("5. PlantVillage dataset provides training data")
            logger.info("6. Responses are channel-specific (text/rich media)")
            
            logger.info("\n" + "=" * 60)
            logger.info("SECURITY & PRIVACY")
            logger.info("=" * 60)
            logger.info("\n1. Images encrypted in transit (HTTPS)")
            logger.info("2. S3 bucket encrypted at rest (KMS)")
            logger.info("3. User-specific folders in S3")
            logger.info("4. Automatic deletion after 90 days (lifecycle policy)")
            logger.info("5. No PII stored with images")
        else:
            logger.warning("No test images found in data/plantvillage/test/test/")
    else:
        logger.warning("Test image directory not found")
        logger.info("\nTo test with real images:")
        logger.info("1. Place test images in data/plantvillage/test/test/")
        logger.info("2. Run this script again")


if __name__ == "__main__":
    main()
