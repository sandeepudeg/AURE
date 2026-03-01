#!/usr/bin/env python3
"""
Simple Streamlit Deployment to AWS App Runner
"""

import boto3
import subprocess
import time
import sys

# Configuration
AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "188238313375"
ECR_REPO_NAME = "ure-streamlit-ui"
APP_RUNNER_SERVICE_NAME = "ure-streamlit-service"
API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

ECR_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}"

print("\n" + "=" * 60)
print("URE MVP - Deploy Streamlit to AWS App Runner")
print("=" * 60)
print(f"\nECR URI: {ECR_URI}")
print(f"API Endpoint: {API_ENDPOINT}\n")

# AWS clients
apprunner = boto3.client('apprunner', region_name=AWS_REGION)
ecr = boto3.client('ecr', region_name=AWS_REGION)

# Step 1: Verify ECR repository
print("Step 1: Verifying ECR repository...")
try:
    ecr.describe_repositories(repositoryNames=[ECR_REPO_NAME])
    print("✓ ECR repository exists")
except:
    print("Creating ECR repository...")
    ecr.create_repository(repositoryName=ECR_REPO_NAME)
    print("✓ ECR repository created")

# Step 2: Check if image exists
print("\nStep 2: Checking Docker image...")
try:
    images = ecr.list_images(repositoryName=ECR_REPO_NAME)
    if images['imageIds']:
        print(f"✓ Found {len(images['imageIds'])} image(s) in ECR")
    else:
        print("⚠ No images found. Please push the Docker image first:")
        print(f"  docker push {ECR_URI}:latest")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error checking images: {e}")
    sys.exit(1)

# Step 3: Get IAM role ARN
print("\nStep 3: Getting IAM role for ECR access...")
iam = boto3.client('iam')
try:
    role_response = iam.get_role(RoleName='AppRunnerECRAccessRole')
    access_role_arn = role_response['Role']['Arn']
    print(f"✓ Using IAM role: {access_role_arn}")
except:
    print("✗ IAM role not found. Please run: py scripts/create_apprunner_role.py")
    sys.exit(1)

# Step 4: Create or update App Runner service
print("\nStep 4: Creating/Updating App Runner service...")

service_config = {
    'ServiceName': APP_RUNNER_SERVICE_NAME,
    'SourceConfiguration': {
        'ImageRepository': {
            'ImageIdentifier': f'{ECR_URI}:latest',
            'ImageRepositoryType': 'ECR',
            'ImageConfiguration': {
                'Port': '8501',
                'RuntimeEnvironmentVariables': {
                    'USE_API_MODE': 'true',
                    'API_ENDPOINT': API_ENDPOINT
                }
            }
        },
        'AuthenticationConfiguration': {
            'AccessRoleArn': access_role_arn
        },
        'AutoDeploymentsEnabled': True
    },
    'InstanceConfiguration': {
        'Cpu': '1 vCPU',
        'Memory': '2 GB'
    },
    'HealthCheckConfiguration': {
        'Protocol': 'HTTP',
        'Path': '/_stcore/health',
        'Interval': 10,
        'Timeout': 5,
        'HealthyThreshold': 1,
        'UnhealthyThreshold': 5
    }
}

try:
    # Check if service exists
    services = apprunner.list_services()
    existing_service = None
    
    for service in services.get('ServiceSummaryList', []):
        if service['ServiceName'] == APP_RUNNER_SERVICE_NAME:
            existing_service = service['ServiceArn']
            break
    
    if existing_service:
        print(f"Updating existing service: {existing_service}")
        response = apprunner.update_service(
            ServiceArn=existing_service,
            SourceConfiguration=service_config['SourceConfiguration'],
            InstanceConfiguration=service_config['InstanceConfiguration'],
            HealthCheckConfiguration=service_config['HealthCheckConfiguration']
        )
        service_arn = existing_service
    else:
        print("Creating new service...")
        response = apprunner.create_service(**service_config)
        service_arn = response['Service']['ServiceArn']
    
    print(f"✓ Service ARN: {service_arn}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 5: Wait for service to be ready
print("\nStep 5: Waiting for service to be ready...")
print("This may take 3-5 minutes...\n")

max_attempts = 40
attempt = 0

while attempt < max_attempts:
    time.sleep(15)
    attempt += 1
    
    try:
        service = apprunner.describe_service(ServiceArn=service_arn)
        status = service['Service']['Status']
        
        print(f"  Attempt {attempt}/{max_attempts} - Status: {status}")
        
        if status == 'RUNNING':
            service_url = service['Service']['ServiceUrl']
            print(f"\n✓ Service is running!")
            print("\n" + "=" * 60)
            print("DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"\nYour Streamlit UI is live at:")
            print(f"  https://{service_url}")
            print(f"\nService Details:")
            print(f"  Name: {APP_RUNNER_SERVICE_NAME}")
            print(f"  ARN: {service_arn}")
            print(f"  Region: {AWS_REGION}")
            print("\n" + "=" * 60)
            break
        elif status in ['CREATE_FAILED', 'UPDATE_FAILED']:
            print(f"\n✗ Deployment failed with status: {status}")
            sys.exit(1)
    except Exception as e:
        print(f"  Error checking status: {e}")

if attempt >= max_attempts:
    print("\n⚠ Deployment is taking longer than expected.")
    print("Check AWS Console for status:")
    print(f"  https://console.aws.amazon.com/apprunner/home?region={AWS_REGION}#/services")
