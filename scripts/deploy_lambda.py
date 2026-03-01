#!/usr/bin/env python3
"""
Deploy Lambda Function for URE MVP
"""

import boto3
import zipfile
import os
import json
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LAMBDA_FUNCTION_NAME = "ure-mvp-handler"
LAMBDA_ROLE_NAME = "ure-lambda-execution-role"
LAMBDA_RUNTIME = "python3.11"
LAMBDA_TIMEOUT = 300  # 5 minutes
LAMBDA_MEMORY = 512  # MB

# AWS clients
lambda_client = boto3.client('lambda', region_name='us-east-1')
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

# Get account ID
account_id = sts_client.get_caller_identity()['Account']


def create_lambda_role():
    """Create IAM role for Lambda execution"""
    logger.info("Creating Lambda execution role...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Execution role for URE MVP Lambda function"
        )
        role_arn = response['Role']['Arn']
        logger.info(f"✓ Created role: {role_arn}")
        
        # Attach policies
        policies = [
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
        ]
        
        for policy_arn in policies:
            iam_client.attach_role_policy(
                RoleName=LAMBDA_ROLE_NAME,
                PolicyArn=policy_arn
            )
            logger.info(f"✓ Attached policy: {policy_arn}")
        
        # Wait for role to be ready
        import time
        logger.info("Waiting for role to propagate...")
        time.sleep(10)
        
        return role_arn
    
    except iam_client.exceptions.EntityAlreadyExistsException:
        logger.info("Role already exists, using existing role")
        response = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        return response['Role']['Arn']


def create_deployment_package():
    """Create Lambda deployment package"""
    logger.info("Creating deployment package...")
    
    # Create temp directory
    temp_dir = Path("temp_lambda_package")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy source code
    src_dir = Path("src")
    for item in src_dir.rglob("*.py"):
        if "__pycache__" not in str(item):
            relative_path = item.relative_to(src_dir)
            dest_path = temp_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)
    
    # Copy .env file
    if Path(".env").exists():
        shutil.copy2(".env", temp_dir / ".env")
    
    # Install dependencies
    logger.info("Installing dependencies...")
    os.system(f"pip install -r requirements-lambda.txt -t {temp_dir} --quiet")
    
    # Create zip file
    zip_path = Path("lambda_deployment.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    logger.info("Creating zip file...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(temp_dir)
                zipf.write(file, arcname)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    logger.info(f"✓ Created deployment package: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return zip_path


def deploy_lambda_function(role_arn, zip_path):
    """Deploy or update Lambda function"""
    logger.info("Deploying Lambda function...")
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    # Environment variables
    env_vars = {
        'DYNAMODB_TABLE_NAME': 'ure-conversations',
        'DYNAMODB_USER_TABLE': 'ure-user-profiles',
        'DYNAMODB_VILLAGE_TABLE': 'ure-village-amenities',
        'S3_BUCKET_NAME': f'ure-mvp-data-us-east-1-{account_id}',
        'BEDROCK_KB_ID': os.getenv('BEDROCK_KB_ID', ''),
        'BEDROCK_MODEL_ID': os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-pro-v1:0'),
        'BEDROCK_REGION': 'us-east-1',
        'LOG_LEVEL': 'INFO'
    }
    
    try:
        # Try to update existing function
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        logger.info(f"✓ Updated existing function: {response['FunctionArn']}")
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime=LAMBDA_RUNTIME,
            Timeout=LAMBDA_TIMEOUT,
            MemorySize=LAMBDA_MEMORY,
            Environment={'Variables': env_vars}
        )
        logger.info("✓ Updated function configuration")
        
        return response['FunctionArn']
    
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        logger.info("Creating new Lambda function...")
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime=LAMBDA_RUNTIME,
            Role=role_arn,
            Handler='aws.lambda_handler.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=LAMBDA_TIMEOUT,
            MemorySize=LAMBDA_MEMORY,
            Environment={'Variables': env_vars},
            Tags={
                'Project': 'URE-MVP',
                'Environment': 'Production'
            }
        )
        logger.info(f"✓ Created function: {response['FunctionArn']}")
        return response['FunctionArn']


def create_api_gateway():
    """Create API Gateway REST API"""
    logger.info("Creating API Gateway...")
    
    apigw_client = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Create REST API
        api_response = apigw_client.create_rest_api(
            name='ure-mvp-api',
            description='API for URE MVP',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api_response['id']
        logger.info(f"✓ Created API: {api_id}")
        
        # Get root resource
        resources = apigw_client.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create /query resource
        resource_response = apigw_client.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='query'
        )
        resource_id = resource_response['id']
        
        # Create POST method
        apigw_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Get Lambda ARN
        lambda_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:{LAMBDA_FUNCTION_NAME}"
        
        # Set Lambda integration
        apigw_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        # Add Lambda permission
        lambda_client.add_permission(
            FunctionName=LAMBDA_FUNCTION_NAME,
            StatementId='apigateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
        )
        
        # Deploy API
        deployment = apigw_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/query"
        logger.info(f"✓ API deployed: {api_url}")
        
        return api_url
    
    except Exception as e:
        logger.error(f"Failed to create API Gateway: {e}")
        return None


def main():
    """Main deployment function"""
    logger.info("\n" + "=" * 60)
    logger.info("URE MVP LAMBDA DEPLOYMENT")
    logger.info("=" * 60)
    
    try:
        # Step 1: Create IAM role
        role_arn = create_lambda_role()
        
        # Step 2: Create deployment package
        zip_path = create_deployment_package()
        
        # Step 3: Deploy Lambda function
        function_arn = deploy_lambda_function(role_arn, zip_path)
        
        # Step 4: Create API Gateway
        api_url = create_api_gateway()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("DEPLOYMENT COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Lambda Function: {function_arn}")
        if api_url:
            logger.info(f"API Endpoint: {api_url}")
        logger.info("\nTest with:")
        logger.info(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"user_id":"test","query":"Hello"}}\'')
        
        # Cleanup
        if zip_path.exists():
            zip_path.unlink()
            logger.info("\n✓ Cleaned up deployment package")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ Deployment failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
