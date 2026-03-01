#!/usr/bin/env python3
"""
Production Deployment Script for URE MVP
Automates the complete deployment process to AWS
"""

import os
import sys
import boto3
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProductionDeployer:
    def __init__(self, stack_name='ure-mvp-stack', region='us-east-1'):
        self.stack_name = stack_name
        self.region = region
        self.cf_client = boto3.client('cloudformation', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check AWS credentials
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Account: {identity['Account']}")
            print(f"✅ AWS User: {identity['Arn']}")
        except Exception as e:
            print(f"❌ AWS credentials not configured: {e}")
            return False
        
        # Check required environment variables
        required_vars = [
            'BEDROCK_KB_ID',
            'BEDROCK_GUARDRAIL_ID',
            'OPENWEATHER_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ All environment variables configured")
        
        # Check CloudFormation template exists
        template_path = Path('cloudformation/ure-infrastructure.yaml')
        if not template_path.exists():
            print(f"❌ CloudFormation template not found: {template_path}")
            return False
        
        print(f"✅ CloudFormation template found: {template_path}")
        
        return True
    
    def deploy_cloudformation(self, alarm_email=None, wait=True):
        """Deploy CloudFormation stack"""
        print(f"\n📦 Deploying CloudFormation stack: {self.stack_name}")
        
        template_path = Path('cloudformation/ure-infrastructure.yaml')
        with open(template_path, 'r') as f:
            template_body = f.read()
        
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
                'ParameterValue': os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-pro-v1:0')
            },
            {
                'ParameterKey': 'BedrockKnowledgeBaseId',
                'ParameterValue': os.getenv('BEDROCK_KB_ID')
            },
            {
                'ParameterKey': 'BedrockGuardrailId',
                'ParameterValue': os.getenv('BEDROCK_GUARDRAIL_ID', '')
            },
            {
                'ParameterKey': 'LambdaReservedConcurrency',
                'ParameterValue': '100'
            },
            {
                'ParameterKey': 'ApiThrottleRateLimit',
                'ParameterValue': '1000'
            },
            {
                'ParameterKey': 'ApiThrottleBurstLimit',
                'ParameterValue': '2000'
            }
        ]
        
        if alarm_email:
            parameters.append({
                'ParameterKey': 'AlarmEmail',
                'ParameterValue': alarm_email
            })
        
        try:
            # Check if stack exists
            try:
                self.cf_client.describe_stacks(StackName=self.stack_name)
                stack_exists = True
                print(f"📝 Stack {self.stack_name} exists, updating...")
            except self.cf_client.exceptions.ClientError:
                stack_exists = False
                print(f"🆕 Creating new stack: {self.stack_name}")
            
            if stack_exists:
                response = self.cf_client.update_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_NAMED_IAM'],
                    Tags=[
                        {'Key': 'Project', 'Value': 'URE-MVP'},
                        {'Key': 'Environment', 'Value': 'dev'}
                    ]
                )
                print(f"✅ Stack update initiated: {response['StackId']}")
                waiter_type = 'stack_update_complete'
            else:
                response = self.cf_client.create_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_NAMED_IAM'],
                    Tags=[
                        {'Key': 'Project', 'Value': 'URE-MVP'},
                        {'Key': 'Environment', 'Value': 'dev'}
                    ]
                )
                print(f"✅ Stack creation initiated: {response['StackId']}")
                waiter_type = 'stack_create_complete'
            
            if wait:
                print(f"⏳ Waiting for stack {waiter_type.replace('_', ' ')}...")
                waiter = self.cf_client.get_waiter(waiter_type)
                waiter.wait(
                    StackName=self.stack_name,
                    WaiterConfig={'Delay': 30, 'MaxAttempts': 60}
                )
                print("✅ Stack deployment complete!")
                return True
            
            return True
            
        except self.cf_client.exceptions.ClientError as e:
            if 'No updates are to be performed' in str(e):
                print("ℹ️  No updates needed - stack is already up to date")
                return True
            else:
                print(f"❌ CloudFormation deployment failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def get_stack_outputs(self):
        """Get CloudFormation stack outputs"""
        try:
            response = self.cf_client.describe_stacks(StackName=self.stack_name)
            outputs = response['Stacks'][0].get('Outputs', [])
            
            output_dict = {}
            for output in outputs:
                output_dict[output['OutputKey']] = output['OutputValue']
            
            return output_dict
        except Exception as e:
            print(f"❌ Failed to get stack outputs: {e}")
            return {}
    
    def deploy_lambda_code(self):
        """Deploy Lambda function code"""
        print("\n🚀 Deploying Lambda function code...")
        
        # Get Lambda function name from stack outputs
        outputs = self.get_stack_outputs()
        lambda_arn = outputs.get('LambdaFunctionArn')
        
        if not lambda_arn:
            print("❌ Lambda function ARN not found in stack outputs")
            return False
        
        function_name = lambda_arn.split(':')[-1]
        
        # Package Lambda code
        print("📦 Packaging Lambda code...")
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            zip_path = tmp_file.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add source code
            src_dir = Path('src')
            for file_path in src_dir.rglob('*.py'):
                arcname = file_path.relative_to('.')
                zipf.write(file_path, arcname)
            
            # Add requirements (if needed)
            # Note: For production, use Lambda layers for dependencies
        
        # Upload to Lambda
        print(f"📤 Uploading code to Lambda function: {function_name}")
        try:
            with open(zip_path, 'rb') as f:
                zip_content = f.read()
            
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
            print("✅ Lambda code deployed successfully!")
            
            # Clean up
            os.unlink(zip_path)
            
            return True
        except Exception as e:
            print(f"❌ Lambda code deployment failed: {e}")
            return False
    
    def test_deployment(self):
        """Test the deployed API"""
        print("\n🧪 Testing deployment...")
        
        outputs = self.get_stack_outputs()
        api_url = outputs.get('ApiGatewayUrl')
        
        if not api_url:
            print("❌ API Gateway URL not found in stack outputs")
            return False
        
        print(f"📍 API Gateway URL: {api_url}")
        
        # Test with a simple query
        import requests
        
        test_payload = {
            'user_id': 'test_user',
            'query': 'What are the symptoms of tomato late blight?',
            'language': 'en'
        }
        
        try:
            print("📤 Sending test request...")
            response = requests.post(api_url, json=test_payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ API test successful!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    def print_summary(self):
        """Print deployment summary"""
        print("\n" + "="*60)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*60)
        
        outputs = self.get_stack_outputs()
        
        if outputs:
            print("\n🔗 Stack Outputs:")
            for key, value in outputs.items():
                print(f"  {key}: {value}")
        
        print("\n✅ Deployment complete!")
        print("\n📝 Next Steps:")
        print("  1. Test the API Gateway endpoint")
        print("  2. Deploy Streamlit UI")
        print("  3. Start MCP servers")
        print("  4. Begin farmer onboarding")
        print("\n📚 Documentation:")
        print("  - Deployment Guide: COMPLETE_DEPLOYMENT_GUIDE.md")
        print("  - API Testing: Use the API Gateway URL above")
        print("  - Monitoring: Check CloudWatch dashboard in AWS Console")


def main():
    parser = argparse.ArgumentParser(description='Deploy URE MVP to AWS Production')
    parser.add_argument('--stack-name', default='ure-mvp-stack', help='CloudFormation stack name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--alarm-email', help='Email address for CloudWatch alarms')
    parser.add_argument('--skip-lambda', action='store_true', help='Skip Lambda code deployment')
    parser.add_argument('--skip-test', action='store_true', help='Skip API testing')
    parser.add_argument('--no-wait', action='store_true', help='Do not wait for stack completion')
    
    args = parser.parse_args()
    
    deployer = ProductionDeployer(stack_name=args.stack_name, region=args.region)
    
    # Check prerequisites
    if not deployer.check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix the issues and try again.")
        sys.exit(1)
    
    # Deploy CloudFormation stack
    if not deployer.deploy_cloudformation(alarm_email=args.alarm_email, wait=not args.no_wait):
        print("\n❌ CloudFormation deployment failed.")
        sys.exit(1)
    
    # Deploy Lambda code
    if not args.skip_lambda:
        if not deployer.deploy_lambda_code():
            print("\n⚠️  Lambda code deployment failed, but stack is deployed.")
    
    # Test deployment
    if not args.skip_test:
        deployer.test_deployment()
    
    # Print summary
    deployer.print_summary()


if __name__ == '__main__':
    main()
