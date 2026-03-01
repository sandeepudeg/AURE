#!/usr/bin/env python3
"""
Deploy Lambda Function to Mumbai (ap-south-1)
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

# Configuration for Mumbai
AWS_REGION = "ap-south-1"
LAMBDA_FUNCTION_NAME = "ure-mvp-handler-mumbai"
LAMBDA_ROLE_NAME = "ure-lambda-execution-role-mumbai"
LAMBDA_RUNTIME = "python3.11"
LAMBDA_TIMEOUT = 300
LAMBDA_MEMORY = 512

# AWS clients for Mumbai
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

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
            Description="Execution role for URE MVP Lambda in Mumbai"
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
        
        import time
        logger.info("Waiting for role to propagate...")
        time.sleep(10)
        
        return role_arn
    
    except iam_client.exceptions.EntityAlreadyExistsException:
        logger.info("Role already exists, using existing role")
        response = iam_client.get_role(RoleName=LAMBDA_ROLE_NAME)
        return response['Role']['Arn']


def create_lambda_layer():
    """Create Lambda Layer with dependencies"""
    logger.info("Creating Lambda Layer...")
    
    layer_dir = Path("lambda_layer")
    python_dir = layer_dir / "python"
    
    if python_dir.exists():
        logger.info("✓ Lambda layer directory exists")
        
        # Create zip file
        zip_path = Path("lambda_layer.zip")
        if zip_path.exists():
            zip_path.unlink()
        
        logger.info("Creating layer zip file...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in python_dir.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(layer_dir)
                    zipf.write(file, arcname)
        
        logger.info(f"✓ Created layer package: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.2f} MB)")
        
        # Upload layer
        with open(zip_path, 'rb') as f:
            layer_content = f.read()
        
        try:
            response = lambda_client.publish_layer_version(
                LayerName='ure-dependencies-mumbai',
                Description='Dependencies for URE MVP in Mumbai',
                Content={'ZipFile': layer_content},
                CompatibleRuntimes=[LAMBDA_RUNTIME]
            )
            layer_arn = response['LayerVersionArn']
            logger.info(f"✓ Published layer: {layer_arn}")
            
            # Cleanup
            zip_path.unlink()
            
            return layer_arn
        except Exception as e:
            logger.error(f"Failed to publish layer: {e}")
            return None
    else:
        logger.warning("Lambda layer directory not found, skipping layer creation")
        return None


def create_deployment_package():
    """Create Lambda deployment package"""
    logger.info("Creating deployment package...")
    
    temp_dir = Path("temp_lambda_mumbai")
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
    
    # Create zip file
    zip_path = Path("lambda_mumbai.zip")
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


def deploy_lambda_function(role_arn, zip_path, layer_arn=None):
    """Deploy or update Lambda function"""
    logger.info("Deploying Lambda function to Mumbai...")
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    env_vars = {
        'DYNAMODB_TABLE_NAME': 'ure-conversations-mumbai',
        'DYNAMODB_USER_TABLE': 'ure-user-profiles-mumbai',
        'DYNAMODB_VILLAGE_TABLE': 'ure-village-amenities-mumbai',
        'S3_BUCKET_NAME': f'ure-mvp-data-mumbai-{account_id}',
        'BEDROCK_KB_ID': os.getenv('BEDROCK_KB_ID', ''),
        'BEDROCK_MODEL_ID': 'apac.amazon.nova-lite-v1:0',  # Use APAC model for Mumbai
        'BEDROCK_REGION': 'ap-south-1',
        'LOG_LEVEL': 'INFO'
    }
    
    try:
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        logger.info(f"✓ Updated existing function: {response['FunctionArn']}")
        
        # Wait for the code update to complete
        import time
        logger.info("Waiting for code update to complete...")
        time.sleep(5)
        
        # Wait for function to be ready
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)
        logger.info("✓ Code update completed")
        
        # Update configuration
        update_config = {
            'FunctionName': LAMBDA_FUNCTION_NAME,
            'Runtime': LAMBDA_RUNTIME,
            'Timeout': LAMBDA_TIMEOUT,
            'MemorySize': LAMBDA_MEMORY,
            'Environment': {'Variables': env_vars}
        }
        
        if layer_arn:
            update_config['Layers'] = [layer_arn]
        
        lambda_client.update_function_configuration(**update_config)
        logger.info("✓ Updated function configuration")
        
        return response['FunctionArn']
    
    except lambda_client.exceptions.ResourceNotFoundException:
        logger.info("Creating new Lambda function...")
        
        create_config = {
            'FunctionName': LAMBDA_FUNCTION_NAME,
            'Runtime': LAMBDA_RUNTIME,
            'Role': role_arn,
            'Handler': 'aws.lambda_handler.lambda_handler',
            'Code': {'ZipFile': zip_content},
            'Timeout': LAMBDA_TIMEOUT,
            'MemorySize': LAMBDA_MEMORY,
            'Environment': {'Variables': env_vars},
            'Tags': {
                'Project': 'URE-MVP',
                'Environment': 'Production',
                'Region': 'Mumbai'
            }
        }
        
        if layer_arn:
            create_config['Layers'] = [layer_arn]
        
        response = lambda_client.create_function(**create_config)
        logger.info(f"✓ Created function: {response['FunctionArn']}")
        return response['FunctionArn']


def create_api_gateway():
    """Create API Gateway in Mumbai"""
    logger.info("Creating API Gateway in Mumbai...")
    
    apigw_client = boto3.client('apigateway', region_name=AWS_REGION)
    
    try:
        # Create REST API
        api_response = apigw_client.create_rest_api(
            name='ure-mvp-api-mumbai',
            description='API for URE MVP in Mumbai',
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
        
        # Set Lambda integration
        lambda_arn = f"arn:aws:lambda:{AWS_REGION}:{account_id}:function:{LAMBDA_FUNCTION_NAME}"
        
        apigw_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        # Add Lambda permission
        lambda_client.add_permission(
            FunctionName=LAMBDA_FUNCTION_NAME,
            StatementId='apigateway-invoke-mumbai',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:{AWS_REGION}:{account_id}:{api_id}/*/*"
        )
        
        # Deploy API
        apigw_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        api_url = f"https://{api_id}.execute-api.{AWS_REGION}.amazonaws.com/prod/query"
        logger.info(f"✓ API deployed: {api_url}")
        
        return api_url
    
    except Exception as e:
        logger.error(f"Failed to create API Gateway: {e}")
        return None


def create_s3_bucket():
    """Create S3 bucket in Mumbai"""
    logger.info("Creating S3 bucket in Mumbai...")
    
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    bucket_name = f'ure-mvp-data-mumbai-{account_id}'
    
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
        )
        logger.info(f"✓ Created S3 bucket: {bucket_name}")
        return bucket_name
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        logger.info(f"✓ S3 bucket already exists: {bucket_name}")
        return bucket_name
    except Exception as e:
        logger.error(f"Failed to create S3 bucket: {e}")
        return None


def create_dynamodb_tables():
    """Create DynamoDB tables in Mumbai"""
    logger.info("Creating DynamoDB tables in Mumbai...")
    
    dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)
    
    tables = [
        {
            'TableName': 'ure-conversations-mumbai',
            'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'ure-user-profiles-mumbai',
            'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'ure-village-amenities-mumbai',
            'KeySchema': [{'AttributeName': 'village_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'village_id', 'AttributeType': 'S'}]
        }
    ]
    
    created_tables = []
    
    for table_config in tables:
        try:
            dynamodb_client.create_table(
                TableName=table_config['TableName'],
                KeySchema=table_config['KeySchema'],
                AttributeDefinitions=table_config['AttributeDefinitions'],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'URE-MVP'},
                    {'Key': 'Region', 'Value': 'Mumbai'}
                ]
            )
            logger.info(f"✓ Created table: {table_config['TableName']}")
            created_tables.append(table_config['TableName'])
        except dynamodb_client.exceptions.ResourceInUseException:
            logger.info(f"✓ Table already exists: {table_config['TableName']}")
            created_tables.append(table_config['TableName'])
        except Exception as e:
            logger.error(f"Failed to create table {table_config['TableName']}: {e}")
    
    return created_tables


def main():
    """Main deployment function"""
    logger.info("\n" + "=" * 60)
    logger.info("URE MVP - DEPLOY TO MUMBAI (ap-south-1)")
    logger.info("=" * 60)
    
    try:
        # Step 1: Create DynamoDB tables
        logger.info("\nStep 1: Creating DynamoDB tables...")
        tables = create_dynamodb_tables()
        
        # Step 2: Create S3 bucket
        logger.info("\nStep 2: Creating S3 bucket...")
        bucket = create_s3_bucket()
        
        # Step 3: Create IAM role
        logger.info("\nStep 3: Creating IAM role...")
        role_arn = create_lambda_role()
        
        # Step 4: Create Lambda Layer
        logger.info("\nStep 4: Creating Lambda Layer...")
        layer_arn = create_lambda_layer()
        
        # Step 5: Create deployment package
        logger.info("\nStep 5: Creating deployment package...")
        zip_path = create_deployment_package()
        
        # Step 6: Deploy Lambda function
        logger.info("\nStep 6: Deploying Lambda function...")
        function_arn = deploy_lambda_function(role_arn, zip_path, layer_arn)
        
        # Step 7: Create API Gateway
        logger.info("\nStep 7: Creating API Gateway...")
        api_url = create_api_gateway()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("MUMBAI DEPLOYMENT COMPLETE")
        logger.info("=" * 60)
        logger.info(f"\nRegion: {AWS_REGION}")
        logger.info(f"Lambda Function: {function_arn}")
        logger.info(f"API Endpoint: {api_url}")
        logger.info(f"S3 Bucket: {bucket}")
        logger.info(f"DynamoDB Tables: {', '.join(tables)}")
        
        logger.info("\n✓ All resources deployed to Mumbai!")
        logger.info("\nTest with:")
        logger.info(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"user_id":"test","query":"Hello"}}\'')
        
        # Save endpoint to file
        with open('MUMBAI_ENDPOINT.txt', 'w') as f:
            f.write(api_url)
        logger.info("\n✓ API endpoint saved to MUMBAI_ENDPOINT.txt")
        
        # Cleanup
        if zip_path.exists():
            zip_path.unlink()
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
