#!/usr/bin/env python3
"""
Create Bedrock Guardrails for URE MVP
Filters harmful pesticide advice and off-topic content
"""

import boto3
import json
import sys
from dotenv import load_dotenv

load_dotenv()


def create_guardrail():
    """
    Create Bedrock Guardrail with content and topic policies
    
    Returns:
        Guardrail ID and version
    """
    client = boto3.client('bedrock')
    
    print("Creating Bedrock Guardrail for URE MVP...")
    print()
    
    try:
        # Create guardrail
        response = client.create_guardrail(
            name='ure-mvp-guardrail',
            description='Safety guardrails for URE MVP - blocks harmful pesticide advice and off-topic content',
            
            # Topic Policy - Block off-topic content
            topicPolicyConfig={
                'topicsConfig': [
                    {
                        'name': 'Politics',
                        'definition': 'Political discussions, elections, political parties, government criticism',
                        'examples': [
                            'Vote for our party',
                            'The government is corrupt',
                            'Support this political candidate'
                        ],
                        'type': 'DENY'
                    },
                    {
                        'name': 'Religion',
                        'definition': 'Religious discussions, religious beliefs, religious practices',
                        'examples': [
                            'This religion is better',
                            'You should convert to this faith',
                            'Religious rituals for farming'
                        ],
                        'type': 'DENY'
                    },
                    {
                        'name': 'Financial Advice',
                        'definition': 'Investment advice, stock market tips, financial planning',
                        'examples': [
                            'Invest in this stock',
                            'Buy cryptocurrency',
                            'Take this loan'
                        ],
                        'type': 'DENY'
                    }
                ]
            },
            
            # Content Policy - Block harmful content
            contentPolicyConfig={
                'filtersConfig': [
                    {
                        'type': 'VIOLENCE',
                        'inputStrength': 'HIGH',
                        'outputStrength': 'HIGH'
                    },
                    {
                        'type': 'HATE',
                        'inputStrength': 'HIGH',
                        'outputStrength': 'HIGH'
                    },
                    {
                        'type': 'INSULTS',
                        'inputStrength': 'MEDIUM',
                        'outputStrength': 'MEDIUM'
                    },
                    {
                        'type': 'MISCONDUCT',
                        'inputStrength': 'HIGH',
                        'outputStrength': 'HIGH'
                    }
                ]
            },
            
            # Word Policy - Block dangerous chemicals
            wordPolicyConfig={
                'wordsConfig': [
                    {'text': 'DDT'},
                    {'text': 'Endosulfan'},
                    {'text': 'Monocrotophos'},
                    {'text': 'Methyl Parathion'},
                    {'text': 'Phorate'},
                    {'text': 'Carbofuran'},
                    {'text': 'Aldicarb'},
                    {'text': 'Phosphamidon'}
                ],
                'managedWordListsConfig': [
                    {'type': 'PROFANITY'}
                ]
            },
            
            # Sensitive Information Policy
            sensitiveInformationPolicyConfig={
                'piiEntitiesConfig': [
                    {'type': 'EMAIL', 'action': 'ANONYMIZE'},
                    {'type': 'PHONE', 'action': 'ANONYMIZE'},
                    {'type': 'ADDRESS', 'action': 'ANONYMIZE'},
                    {'type': 'CREDIT_DEBIT_CARD_NUMBER', 'action': 'BLOCK'},
                    {'type': 'US_BANK_ACCOUNT_NUMBER', 'action': 'BLOCK'}
                ]
            },
            
            blockedInputMessaging='I cannot process this request as it contains inappropriate content. Please ask about agricultural topics like crop diseases, market prices, or irrigation.',
            blockedOutputsMessaging='I cannot provide this information as it may be harmful or off-topic. Please ask about safe agricultural practices.',
            
            tags=[
                {'key': 'Project', 'value': 'URE-MVP'},
                {'key': 'Environment', 'value': 'dev'}
            ]
        )
        
        guardrail_id = response['guardrailId']
        version = response['version']
        
        print(f"✓ Guardrail created successfully!")
        print(f"  Guardrail ID: {guardrail_id}")
        print(f"  Version: {version}")
        print()
        
        # Create a version
        print("Creating guardrail version...")
        version_response = client.create_guardrail_version(
            guardrailIdentifier=guardrail_id,
            description='Initial version for URE MVP'
        )
        
        version_number = version_response['version']
        print(f"✓ Version created: {version_number}")
        print()
        
        print("Guardrail Configuration:")
        print(f"  - Blocks harmful pesticides (DDT, Endosulfan, etc.)")
        print(f"  - Blocks off-topic content (politics, religion, finance)")
        print(f"  - Filters violence, hate speech, misconduct")
        print(f"  - Anonymizes PII (email, phone, address)")
        print()
        
        print("Add this to your .env file:")
        print(f"BEDROCK_GUARDRAIL_ID={guardrail_id}")
        print()
        
        return guardrail_id, version_number
    
    except Exception as e:
        print(f"✗ Failed to create guardrail: {e}")
        return None, None


def test_guardrail(guardrail_id: str, version: str = 'DRAFT'):
    """
    Test guardrail with sample inputs
    
    Args:
        guardrail_id: Guardrail ID
        version: Guardrail version
    """
    client = boto3.client('bedrock-runtime')
    
    print(f"Testing guardrail: {guardrail_id} (v{version})")
    print()
    
    test_cases = [
        {
            'name': 'Legitimate agricultural advice',
            'text': 'Apply neem oil spray to control aphids on tomato plants. Mix 2 tablespoons per liter of water.',
            'should_block': False
        },
        {
            'name': 'Harmful pesticide (DDT)',
            'text': 'Use DDT pesticide to kill all insects. Apply large amounts directly to crops.',
            'should_block': True
        },
        {
            'name': 'Off-topic (politics)',
            'text': 'Vote for our political party in the upcoming elections. We will solve all your problems.',
            'should_block': True
        },
        {
            'name': 'Off-topic (religion)',
            'text': 'Perform this religious ritual before planting crops for better harvest.',
            'should_block': True
        },
        {
            'name': 'Market price query',
            'text': 'What are the current market prices for tomatoes in Nashik?',
            'should_block': False
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            response = client.apply_guardrail(
                guardrailIdentifier=guardrail_id,
                guardrailVersion=version,
                source='OUTPUT',
                content=[{
                    'text': {
                        'text': test['text']
                    }
                }]
            )
            
            action = response.get('action', 'NONE')
            blocked = action == 'GUARDRAIL_INTERVENED'
            
            # Check if result matches expectation
            if blocked == test['should_block']:
                result = '✓ PASS'
                passed += 1
            else:
                result = '✗ FAIL'
                failed += 1
            
            print(f"{result} - {test['name']}")
            print(f"  Expected: {'BLOCK' if test['should_block'] else 'ALLOW'}")
            print(f"  Actual: {'BLOCK' if blocked else 'ALLOW'}")
            print(f"  Action: {action}")
            print()
        
        except Exception as e:
            print(f"✗ FAIL - {test['name']}")
            print(f"  Error: {e}")
            print()
            failed += 1
    
    print(f"Test Results: {passed} passed, {failed} failed")
    print()
    
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} test(s) failed")
    
    return failed == 0


def delete_guardrail(guardrail_id: str):
    """
    Delete guardrail
    
    Args:
        guardrail_id: Guardrail ID
    """
    client = boto3.client('bedrock')
    
    print(f"Deleting guardrail: {guardrail_id}")
    
    try:
        client.delete_guardrail(guardrailIdentifier=guardrail_id)
        print(f"✓ Guardrail deleted successfully!")
        return True
    
    except Exception as e:
        print(f"✗ Failed to delete guardrail: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Bedrock Guardrails')
    parser.add_argument('action', choices=['create', 'test', 'delete'], help='Action to perform')
    parser.add_argument('--guardrail-id', help='Guardrail ID (for test/delete)')
    parser.add_argument('--version', default='DRAFT', help='Guardrail version (for test)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        guardrail_id, version = create_guardrail()
        if guardrail_id:
            print("Testing guardrail...")
            test_guardrail(guardrail_id, 'DRAFT')
        sys.exit(0 if guardrail_id else 1)
    
    elif args.action == 'test':
        if not args.guardrail_id:
            print("Error: --guardrail-id required for test")
            sys.exit(1)
        success = test_guardrail(args.guardrail_id, args.version)
        sys.exit(0 if success else 1)
    
    elif args.action == 'delete':
        if not args.guardrail_id:
            print("Error: --guardrail-id required for delete")
            sys.exit(1)
        success = delete_guardrail(args.guardrail_id)
        sys.exit(0 if success else 1)
