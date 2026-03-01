#!/usr/bin/env python3
"""
Redeploy URE MVP Infrastructure
"""

import boto3
import json
import time
import os
from pathlib import Path

# AWS clients
iam = boto3.client('iam', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')
apigw = boto3.client('apigateway', region_name='us-east-1')
sts = boto3.client('sts')

account_id = sts.get_caller_identity()['Account']

print("=" * 60)
print("URE MVP INFRASTRUCTURE REDEPLOYMENT")
print("=" * 60)

# Step 1: Create IAM Role
print("\n1. Creating IAM Role...")
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    role_response = iam.create_role(
        RoleName='ure-mvp-lambda-role',
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description='Execution role for URE MVP Lambda'
    )
    role_arn = role_response['Role']['Arn']
    print(f"✓ Created role: {role_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    role_response = iam.get_role(RoleName='ure-mvp-lambda-role')
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role already exists: {role_arn}")

# Attach managed policies
print("\n2. Attaching policies...")
managed_policies = [
    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
]

for policy_arn in managed_policies:
    try:
        iam.attach_role_policy(RoleName='ure-mvp-lambda-role', PolicyArn=policy_arn)
        print(f"✓ Attached: {policy_arn}")
    except:
        print(f"  Already attached: {policy_arn}")

# Create inline policies
inline_policies = {
    'DynamoDBAccess': {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Query", "dynamodb:Scan"],
            "Resource": [
                f"arn:aws:dynamodb:us-east-1:{account_id}:table/ure-conversations",
                f"arn:aws:dynamodb:us-east-1:{account_id}:table/ure-user-profiles",
                f"arn:aws:dynamodb:us-east-1:{account_id}:table/ure-village-amenities"
            ]
        }]
    },
    'S3Access': {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
            "Resource": [
                f"arn:aws:s3:::ure-mvp-data-us-east-1-{account_id}",
                f"arn:aws:s3:::ure-mvp-data-us-east-1-{account_id}/*"
            ]
        }]
    },
    'BedrockAccess': {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": ["arn:aws:bedrock:*::foundation-model/*", "arn:aws:bedrock:*:*:inference-profile/*"]
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                "Resource": f"arn:aws:bedrock:us-east-1:{account_id}:knowledge-base/7XROZ6PZIF"
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:ApplyGuardrail"],
                "Resource": f"arn:aws:bedrock:us-east-1:{account_id}:guardrail/*"
            }
        ]
    },
    'TranslateAccess': {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["translate:TranslateText"],
            "Resource": "*"
        }]
    },
    'CloudWatchMetrics': {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["cloudwatch:PutMetricData"],
            "Resource": "*"
        }]
    },
    'KMSAccess': {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey", "kms:DescribeKey"],
            "Resource": f"arn:aws:kms:us-east-1:{account_id}:key/fa333734-c93e-42b9-b84c-c9bb5adf64ba"
        }]
    }
}

for policy_name, policy_doc in inline_policies.items():
    try:
        iam.put_role_policy(
            RoleName='ure-mvp-lambda-role',
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_doc)
        )
        print(f"✓ Created inline policy: {policy_name}")
    except Exception as e:
        print(f"  Error with {policy_name}: {e}")

print("\n3. Waiting for role to propagate...")
time.sleep(10)

# Step 2: Create Lambda Function
print("\n4. Creating Lambda Function...")

# Read the deployment package
lambda_zip_path = Path('lambda_deployment.zip')
if not lambda_zip_path.exists():
    print("✗ lambda_deployment.zip not found!")
    exit(1)

with open(lambda_zip_path, 'rb') as f:
    zip_content = f.read()

env_vars = {
    'DYNAMODB_CONVERSATIONS_TABLE': 'ure-conversations',
    'DYNAMODB_USER_PROFILES_TABLE': 'ure-user-profiles',
    'DYNAMODB_VILLAGE_AMENITIES_TABLE': 'ure-village-amenities',
    'S3_BUCKET_NAME': f'ure-mvp-data-us-east-1-{account_id}',
    'BEDROCK_KB_ID': '7XROZ6PZIF',
    'BEDROCK_GUARDRAIL_ID': 'q6wfsifs9d72',
    'BEDROCK_MODEL_ID': 'us.amazon.nova-pro-v1:0',
    'KMS_KEY_ID': 'arn:aws:kms:us-east-1:188238313375:key/fa333734-c93e-42b9-b84c-c9bb5adf64ba'
}

try:
    lambda_response = lambda_client.create_function(
        FunctionName='ure-mvp-handler',
        Runtime='python3.11',
        Role=role_arn,
        Handler='aws.lambda_handler.lambda_handler',
        Code={'ZipFile': zip_content},
        Timeout=300,
        MemorySize=1024,
        Environment={'Variables': env_vars}
    )
    function_arn = lambda_response['FunctionArn']
    print(f"✓ Created Lambda function: {function_arn}")
except lambda_client.exceptions.ResourceConflictException:
    print("  Lambda function already exists, updating code...")
    lambda_client.update_function_code(
        FunctionName='ure-mvp-handler',
        ZipFile=zip_content
    )
    function_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:ure-mvp-handler"
    print(f"✓ Updated Lambda function: {function_arn}")

# Attach Lambda Layer
print("\n5. Attaching Lambda Layer...")
try:
    lambda_client.update_function_configuration(
        FunctionName='ure-mvp-handler',
        Layers=[f'arn:aws:lambda:us-east-1:{account_id}:layer:ure-dependencies:2']
    )
    print("✓ Attached Lambda layer")
except Exception as e:
    print(f"  Error attaching layer: {e}")

print("\n6. Waiting for Lambda to be ready...")
time.sleep(10)

# Step 3: Create API Gateway
print("\n7. Creating API Gateway...")

try:
    api_response = apigw.create_rest_api(
        name='ure-mvp-api',
        description='API for URE MVP',
        endpointConfiguration={'types': ['REGIONAL']}
    )
    api_id = api_response['id']
    print(f"✓ Created API: {api_id}")
except Exception as e:
    print(f"  Error creating API: {e}")
    # Try to find existing API
    apis = apigw.get_rest_apis()
    for api in apis['items']:
        if api['name'] == 'ure-mvp-api':
            api_id = api['id']
            print(f"  Using existing API: {api_id}")
            break

# Get root resource
resources = apigw.get_resources(restApiId=api_id)
root_id = resources['items'][0]['id']

# Create /query resource
try:
    resource_response = apigw.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='query'
    )
    resource_id = resource_response['id']
    print(f"✓ Created /query resource")
except:
    # Resource might already exist
    for item in resources['items']:
        if item.get('pathPart') == 'query':
            resource_id = item['id']
            print(f"  Using existing /query resource")
            break

# Create POST method
try:
    apigw.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='NONE'
    )
    print("✓ Created POST method")
except:
    print("  POST method already exists")

# Set Lambda integration
lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
try:
    apigw.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=lambda_uri
    )
    print("✓ Created Lambda integration")
except:
    print("  Lambda integration already exists")

# Add Lambda permission
try:
    lambda_client.add_permission(
        FunctionName='ure-mvp-handler',
        StatementId='apigateway-invoke',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
    )
    print("✓ Added Lambda permission")
except:
    print("  Lambda permission already exists")

# Deploy API
try:
    deployment = apigw.create_deployment(
        restApiId=api_id,
        stageName='dev'
    )
    print("✓ Deployed API to 'dev' stage")
except Exception as e:
    print(f"  Error deploying API: {e}")

api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/dev/query"

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE!")
print("=" * 60)
print(f"\nAPI Endpoint: {api_url}")
print(f"Lambda Function: {function_arn}")
print("\nTest with:")
print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"user_id":"test","query":"Hello","language":"en"}}\'')
