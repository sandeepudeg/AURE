#!/usr/bin/env python3
"""
Test Lambda handler locally before deployment
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

# Set Lambda environment variables
os.environ['DYNAMODB_TABLE_NAME'] = 'ure-conversations'
os.environ['DYNAMODB_USER_TABLE'] = 'ure-user-profiles'
os.environ['S3_BUCKET_NAME'] = os.getenv('S3_BUCKET_NAME')
os.environ['BEDROCK_KB_ID'] = os.getenv('BEDROCK_KB_ID')
os.environ['BEDROCK_MODEL_ID'] = os.getenv('BEDROCK_MODEL_ID')
os.environ['BEDROCK_REGION'] = 'us-east-1'

from aws.lambda_handler import lambda_handler
import json


def test_api_gateway_format():
    """Test with API Gateway event format"""
    print("\n" + "=" * 60)
    print("TEST: API Gateway Event Format")
    print("=" * 60)
    
    # Simulate API Gateway event
    event = {
        'body': json.dumps({
            'user_id': 'test_farmer_api',
            'query': 'What are the symptoms of tomato blight?',
            'language': 'en'
        }),
        'headers': {
            'Content-Type': 'application/json'
        },
        'httpMethod': 'POST',
        'path': '/query'
    }
    
    result = lambda_handler(event, None)
    
    print(f"\nStatus Code: {result['statusCode']}")
    print(f"Headers: {result['headers']}")
    
    body = json.loads(result['body'])
    print(f"\nResponse Body:")
    print(f"  User ID: {body.get('user_id')}")
    print(f"  Agent Used: {body.get('agent_used')}")
    print(f"  Response Preview: {body.get('response', '')[:150]}...")
    
    return result['statusCode'] == 200


def test_direct_invocation():
    """Test with direct Lambda invocation format"""
    print("\n" + "=" * 60)
    print("TEST: Direct Lambda Invocation")
    print("=" * 60)
    
    event = {
        'user_id': 'test_farmer_direct',
        'query': 'Tell me about PM-Kisan scheme',
        'language': 'en'
    }
    
    result = lambda_handler(event, None)
    
    print(f"\nStatus Code: {result['statusCode']}")
    
    body = json.loads(result['body'])
    print(f"\nResponse Body:")
    print(f"  User ID: {body.get('user_id')}")
    print(f"  Agent Used: {body.get('agent_used')}")
    print(f"  Response Preview: {body.get('response', '')[:150]}...")
    
    return result['statusCode'] == 200


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LAMBDA HANDLER LOCAL TEST")
    print("=" * 60)
    
    tests = [
        ("API Gateway Format", test_api_gateway_format),
        ("Direct Invocation", test_direct_invocation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} passed")
            else:
                failed += 1
                print(f"\n✗ {test_name} failed")
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - Ready for deployment!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
