#!/usr/bin/env python3
"""
Test Lambda Handler locally
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

# Set environment variables for Lambda
os.environ['DYNAMODB_TABLE_NAME'] = 'ure-conversations'
os.environ['DYNAMODB_USER_TABLE'] = 'ure-user-profiles'
os.environ['S3_BUCKET_NAME'] = os.getenv('S3_BUCKET_NAME', 'ure-mvp-data-us-east-1-188238313375')

from aws.lambda_handler import lambda_handler
import json


def test_text_query():
    """Test 1: Simple text query"""
    print("\n" + "=" * 60)
    print("TEST 1: Text Query")
    print("=" * 60)
    
    event = {
        'user_id': 'test_farmer_001',
        'query': 'What are the symptoms of tomato late blight?',
        'language': 'en'
    }
    
    result = lambda_handler(event, None)
    
    print(f"Status Code: {result['statusCode']}")
    body = json.loads(result['body'])
    print(f"Agent Used: {body.get('agent_used')}")
    print(f"Response Preview: {body.get('response', '')[:200]}...")
    
    return result['statusCode'] == 200


def test_scheme_query():
    """Test 2: Government scheme query"""
    print("\n" + "=" * 60)
    print("TEST 2: Scheme Query")
    print("=" * 60)
    
    event = {
        'user_id': 'test_farmer_002',
        'query': 'What is PM-Kisan scheme and am I eligible?',
        'language': 'en'
    }
    
    result = lambda_handler(event, None)
    
    print(f"Status Code: {result['statusCode']}")
    body = json.loads(result['body'])
    print(f"Agent Used: {body.get('agent_used')}")
    print(f"Response Preview: {body.get('response', '')[:200]}...")
    
    return result['statusCode'] == 200


def test_irrigation_query():
    """Test 3: Irrigation/resource query"""
    print("\n" + "=" * 60)
    print("TEST 3: Irrigation Query")
    print("=" * 60)
    
    event = {
        'user_id': 'test_farmer_003',
        'query': 'When should I irrigate my wheat crop?',
        'language': 'en'
    }
    
    result = lambda_handler(event, None)
    
    print(f"Status Code: {result['statusCode']}")
    body = json.loads(result['body'])
    print(f"Agent Used: {body.get('agent_used')}")
    print(f"Response Preview: {body.get('response', '')[:200]}...")
    
    return result['statusCode'] == 200


def test_image_query():
    """Test 4: Image analysis query"""
    print("\n" + "=" * 60)
    print("TEST 4: Image Analysis Query")
    print("=" * 60)
    
    # Load a test image
    test_image_path = Path("data/plantvillage/test/test/AppleCedarRust1.JPG")
    
    if not test_image_path.exists():
        print("⚠ Test image not found, skipping")
        return True
    
    import base64
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    event = {
        'user_id': 'test_farmer_004',
        'query': 'What disease is this?',
        'image': image_data,
        'language': 'en'
    }
    
    result = lambda_handler(event, None)
    
    print(f"Status Code: {result['statusCode']}")
    body = json.loads(result['body'])
    print(f"Agent Used: {body.get('agent_used')}")
    print(f"Response Preview: {body.get('response', '')[:200]}...")
    
    return result['statusCode'] == 200


def test_conversation_persistence():
    """Test 5: Conversation history persistence"""
    print("\n" + "=" * 60)
    print("TEST 5: Conversation Persistence")
    print("=" * 60)
    
    import boto3
    
    user_id = 'test_farmer_persistence'
    
    # Send multiple queries
    queries = [
        "What is PM-Kisan?",
        "How do I apply?",
        "What documents do I need?"
    ]
    
    for query in queries:
        event = {
            'user_id': user_id,
            'query': query,
            'language': 'en'
        }
        lambda_handler(event, None)
    
    # Check DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('ure-conversations')
    
    response = table.get_item(Key={'user_id': user_id})
    
    if 'Item' in response:
        conversations = response['Item'].get('conversations', [])
        print(f"✓ Stored {len(conversations)} conversations")
        return len(conversations) >= 3
    else:
        print("✗ No conversations found")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LAMBDA HANDLER INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Text Query", test_text_query),
        ("Scheme Query", test_scheme_query),
        ("Irrigation Query", test_irrigation_query),
        ("Image Analysis", test_image_query),
        ("Conversation Persistence", test_conversation_persistence)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} passed")
            else:
                failed += 1
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Lambda Handler Ready!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
