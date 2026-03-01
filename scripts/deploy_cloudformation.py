#!/usr/bin/env python3
"""
Deploy CloudFormation Stack for URE MVP
"""

import boto3
import time
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def deploy_stack(
    stack_name: str,
    template_path: str,
    bedrock_kb_id: str,
    bedrock_guardrail_id: str = '',
    wait: bool = True
):
    """
    Deploy CloudFormation stack
    
    Args:
        stack_name: Stack name
        template_path: Path to CloudFormation template
        bedrock_kb_id: Bedrock Knowledge Base ID
        bedrock_guardrail_id: Bedrock Guardrail ID (optional)
        wait: Wait for stack creation to complete
    """
    client = boto3.client('cloudformation')
    
    # Read template
    with open(template_path, 'r') as f:
        template_body = f.read()
    
    # Prepare parameters
    parameters = [
        {
            'ParameterKey': 'ProjectName',
            'ParameterValue': 'ure-mvp'
        },
        {
            'ParameterKey': 'Environment',
            'ParameterValue': 'dev'
        },
        {
            'ParameterKey': 'BedrockModelId',
            'ParameterValue': 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        },
        {
            'ParameterKey': 'BedrockKnowledgeBaseId',
            'ParameterValue': bedrock_kb_id
        }
    ]
    
    if bedrock_guardrail_id:
        parameters.append({
            'ParameterKey': 'BedrockGuardrailId',
            'ParameterValue': bedrock_guardrail_id
        })
    
    print(f"Deploying CloudFormation stack: {stack_name}")
    print(f"Template: {template_path}")
    print(f"Bedrock KB ID: {bedrock_kb_id}")
    if bedrock_guardrail_id:
        print(f"Bedrock Guardrail ID: {bedrock_guardrail_id}")
    print()
    
    try:
        # Check if stack exists
        try:
            client.describe_stacks(StackName=stack_name)
            stack_exists = True
            print(f"Stack {stack_name} exists - updating...")
        except client.exceptions.ClientError:
            stack_exists = False
            print(f"Stack {stack_name} does not exist - creating...")
        
        # Create or update stack
        if stack_exists:
            response = client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            operation = 'UPDATE'
        else:
            response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                OnFailure='ROLLBACK',
                Tags=[
                    {'Key': 'Project', 'Value': 'URE-MVP'},
                    {'Key': 'Environment', 'Value': 'dev'}
                ]
            )
            operation = 'CREATE'
        
        stack_id = response['StackId']
        print(f"Stack {operation} initiated: {stack_id}")
        print()
        
        if not wait:
            print("Not waiting for stack completion (use --wait to wait)")
            return
        
        # Wait for stack creation/update
        print(f"Waiting for stack {operation.lower()} to complete...")
        waiter_name = 'stack_create_complete' if operation == 'CREATE' else 'stack_update_complete'
        waiter = client.get_waiter(waiter_name)
        
        try:
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 10,
                    'MaxAttempts': 120  # 20 minutes max
                }
            )
            print(f"✓ Stack {operation.lower()} completed successfully!")
            print()
            
            # Get stack outputs
            response = client.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            
            if 'Outputs' in stack:
                print("Stack Outputs:")
                for output in stack['Outputs']:
                    print(f"  {output['OutputKey']}: {output['OutputValue']}")
                print()
            
            return True
        
        except Exception as e:
            print(f"✗ Stack {operation.lower()} failed: {e}")
            
            # Get stack events to show errors
            print("\nRecent stack events:")
            events = client.describe_stack_events(StackName=stack_name)
            for event in events['StackEvents'][:10]:
                status = event['ResourceStatus']
                if 'FAILED' in status:
                    print(f"  {event['LogicalResourceId']}: {status}")
                    if 'ResourceStatusReason' in event:
                        print(f"    Reason: {event['ResourceStatusReason']}")
            
            return False
    
    except Exception as e:
        print(f"✗ Deployment failed: {e}")
        return False


def delete_stack(stack_name: str, wait: bool = True):
    """
    Delete CloudFormation stack
    
    Args:
        stack_name: Stack name
        wait: Wait for deletion to complete
    """
    client = boto3.client('cloudformation')
    
    print(f"Deleting CloudFormation stack: {stack_name}")
    
    try:
        client.delete_stack(StackName=stack_name)
        print(f"Stack deletion initiated")
        
        if not wait:
            print("Not waiting for deletion to complete")
            return
        
        print("Waiting for stack deletion to complete...")
        waiter = client.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 120
            }
        )
        
        print(f"✓ Stack deleted successfully!")
        return True
    
    except Exception as e:
        print(f"✗ Stack deletion failed: {e}")
        return False


def get_stack_outputs(stack_name: str):
    """
    Get CloudFormation stack outputs
    
    Args:
        stack_name: Stack name
    """
    client = boto3.client('cloudformation')
    
    try:
        response = client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        print(f"Stack: {stack_name}")
        print(f"Status: {stack['StackStatus']}")
        print()
        
        if 'Outputs' in stack:
            print("Outputs:")
            for output in stack['Outputs']:
                print(f"  {output['OutputKey']}: {output['OutputValue']}")
        else:
            print("No outputs available")
        
        return stack.get('Outputs', [])
    
    except Exception as e:
        print(f"✗ Failed to get stack outputs: {e}")
        return []


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy URE CloudFormation stack')
    parser.add_argument('action', choices=['deploy', 'delete', 'outputs'], help='Action to perform')
    parser.add_argument('--stack-name', default='ure-mvp-stack', help='Stack name')
    parser.add_argument('--template', default='cloudformation/ure-infrastructure.yaml', help='Template path')
    parser.add_argument('--kb-id', help='Bedrock Knowledge Base ID')
    parser.add_argument('--guardrail-id', default='', help='Bedrock Guardrail ID (optional)')
    parser.add_argument('--wait', action='store_true', help='Wait for operation to complete')
    
    args = parser.parse_args()
    
    if args.action == 'deploy':
        # Get KB ID from environment if not provided
        kb_id = args.kb_id or os.getenv('BEDROCK_KB_ID')
        if not kb_id:
            print("Error: Bedrock Knowledge Base ID required (--kb-id or BEDROCK_KB_ID env var)")
            sys.exit(1)
        
        guardrail_id = args.guardrail_id or os.getenv('BEDROCK_GUARDRAIL_ID', '')
        
        success = deploy_stack(
            stack_name=args.stack_name,
            template_path=args.template,
            bedrock_kb_id=kb_id,
            bedrock_guardrail_id=guardrail_id,
            wait=args.wait
        )
        sys.exit(0 if success else 1)
    
    elif args.action == 'delete':
        success = delete_stack(args.stack_name, wait=args.wait)
        sys.exit(0 if success else 1)
    
    elif args.action == 'outputs':
        get_stack_outputs(args.stack_name)
        sys.exit(0)
