#!/usr/bin/env python3
"""
End-to-End Integration Test
Tests the complete URE system flow
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_environment():
    """Test 1: Verify environment configuration"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Environment Configuration")
    logger.info("=" * 60)
    
    required_vars = [
        'BEDROCK_MODEL_ID',
        'BEDROCK_REGION',
        'BEDROCK_KB_ID',
        'S3_BUCKET_NAME'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✓ {var}: {value}")
        else:
            logger.error(f"✗ {var}: NOT SET")
            missing.append(var)
    
    if missing:
        raise ValueError(f"Missing environment variables: {missing}")
    
    logger.info("✓ All environment variables configured")
    return True


def test_bedrock_connection():
    """Test 2: Verify Bedrock connectivity"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Bedrock Connectivity")
    logger.info("=" * 60)
    
    import boto3
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Simple test query
        response = bedrock_runtime.converse(
            modelId='us.amazon.nova-pro-v1:0',
            messages=[{
                "role": "user",
                "content": [{"text": "Say 'OK' if you can hear me"}]
            }]
        )
        
        output = response['output']['message']['content'][0]['text']
        logger.info(f"✓ Bedrock response: {output}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Bedrock connection failed: {e}")
        raise


def test_knowledge_base():
    """Test 3: Verify Knowledge Base access"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Knowledge Base Access")
    logger.info("=" * 60)
    
    from tools import get_kb_tool
    
    try:
        kb_tool = get_kb_tool()
        logger.info(f"✓ KB Tool initialized with ID: {kb_tool.kb_id}")
        
        # Test query
        result = kb_tool.query_schemes("What is PMKSY scheme?", max_results=2)
        
        if result['success'] and result['count'] > 0:
            logger.info(f"✓ KB query successful: {result['count']} results")
            return True
        else:
            logger.error("✗ KB query returned no results")
            return False
            
    except Exception as e:
        logger.error(f"✗ KB access failed: {e}")
        raise


def test_s3_access():
    """Test 4: Verify S3 bucket access"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: S3 Bucket Access")
    logger.info("=" * 60)
    
    import boto3
    
    try:
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        # List objects in schemes folder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='schemes/',
            MaxKeys=10
        )
        
        count = response.get('KeyCount', 0)
        logger.info(f"✓ S3 accessible: {count} objects in schemes/")
        
        # Check plantvillage folder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='plantvillage/',
            MaxKeys=10
        )
        
        count = response.get('KeyCount', 0)
        logger.info(f"✓ S3 accessible: {count} objects in plantvillage/")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ S3 access failed: {e}")
        raise


def test_dynamodb_access():
    """Test 5: Verify DynamoDB access"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: DynamoDB Access")
    logger.info("=" * 60)
    
    import boto3
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        tables = [
            'ure-conversations',
            'ure-user-profiles',
            'ure-village-amenities'
        ]
        
        for table_name in tables:
            try:
                table = dynamodb.Table(table_name)
                table.load()
                logger.info(f"✓ Table accessible: {table_name}")
            except Exception as e:
                logger.warning(f"⚠ Table not accessible: {table_name} - {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ DynamoDB access failed: {e}")
        raise


def test_agent_text_query():
    """Test 6: Test agent with text query"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Agent Text Query")
    logger.info("=" * 60)
    
    from agents.agri_expert import agri_expert_agent
    
    try:
        query = "What are the symptoms of tomato late blight?"
        logger.info(f"Query: {query}")
        
        response = agri_expert_agent(query)
        logger.info(f"✓ Agent response received ({len(str(response))} chars)")
        logger.info(f"Preview: {str(response)[:150]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Agent query failed: {e}")
        raise


def test_image_analysis():
    """Test 7: Test image analysis"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Image Analysis")
    logger.info("=" * 60)
    
    import boto3
    
    test_image_dir = Path("data/plantvillage/test/test")
    
    if not test_image_dir.exists():
        logger.warning("⚠ Test images not available, skipping")
        return True
    
    test_images = list(test_image_dir.glob("*.JPG"))
    if not test_images:
        logger.warning("⚠ No test images found, skipping")
        return True
    
    try:
        test_image = test_images[0]
        logger.info(f"Testing with: {test_image.name}")
        
        with open(test_image, 'rb') as f:
            image_bytes = f.read()
        
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        response = bedrock_runtime.converse(
            modelId='us.amazon.nova-pro-v1:0',
            messages=[{
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": image_bytes}
                        }
                    },
                    {"text": "Identify the plant disease in one sentence"}
                ]
            }]
        )
        
        output = response['output']['message']['content'][0]['text']
        logger.info(f"✓ Image analysis successful")
        logger.info(f"Result: {output}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Image analysis failed: {e}")
        raise


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("URE END-TO-END INTEGRATION TEST")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Bedrock Connectivity", test_bedrock_connection),
        ("Knowledge Base Access", test_knowledge_base),
        ("S3 Bucket Access", test_s3_access),
        ("DynamoDB Access", test_dynamodb_access),
        ("Agent Text Query", test_agent_text_query),
        ("Image Analysis", test_image_analysis)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"Test failed: {test_name}")
            failed += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    if failed == 0:
        logger.info("\n✓ ALL TESTS PASSED - System Ready!")
        return 0
    else:
        logger.error(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
