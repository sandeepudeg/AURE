#!/usr/bin/env python3
"""
Deploy Streamlit to Singapore (ap-southeast-1) - Closest to India
"""

import boto3
import subprocess
import time
import sys
import os

# Configuration for Singapore
AWS_REGION = "ap-southeast-1"
AWS_ACCOUNT_ID = "188238313375"
ECR_REPO_NAME = "ure-streamlit-ui-singapore"
APP_RUNNER_SERVICE_NAME = "ure-streamlit-singapore"

# API endpoint will be from Mumbai deployment
API_ENDPOINT = os.getenv('MUMBAI_API_ENDPOINT', 'https://YOUR_MUMBAI_API.execute-api.ap-south-1.amazonaws.com/prod/query')

ECR_URI = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO_NAME}"

print("\n" + "=" * 60)
print("URE MVP - Deploy Streamlit to Singapore (ap-southeast-1)")
print("=" * 60)
print(f"\nRegion: {AWS_REGION}")
print(f"ECR URI: {ECR_URI}")
print(f"API Endpoint: {API_ENDPOINT}\n")

# AWS clients for Singapore
apprunner = boto3.client('apprunner', region_name=AWS_REGION)
ecr = boto3.client('ecr', region_name=AWS_REGION)
iam = boto3.client('iam')

# Step 1: Create ECR repository in Singapore
print("Step 1: Creating ECR repository in Singapore...")
try:
    ecr.create_repository(repositoryName=ECR_REPO_NAME)
    print("✓ ECR repository created")
except ecr.exceptions.RepositoryAlreadyExistsException:
    print("✓ ECR repository already exists")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 2: Build and push Docker image
print("\nStep 2: Building and pushing Docker image...")
print("This may take 5-10 minutes...\n")

try:
    # Login to ECR
    print("Logging in to ECR...")
    login_cmd = f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
    result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ ECR login failed: {result.stderr}")
        sys.exit(1)
    print("✓ Logged in to ECR")
    
    # Build Docker image
    print("\nBuilding Docker image...")
    build_cmd = f"docker build -t {ECR_REPO_NAME} ."
    result = subprocess.run(build_cmd, shell=True)
    if result.returncode != 0:
        print("✗ Docker build failed")
        sys.exit(1)
    print("✓ Docker image built")
    
    # Tag image
    print("\nTagging image...")
    tag_cmd = f"docker tag {ECR_REPO_NAME}:latest {ECR_URI}:latest"
    result = subprocess.run(tag_cmd, shell=True)
    if result.returncode != 0:
        print("✗ Docker tag failed")
        sys.exit(1)
    print("✓ Image tagged")
    
    # Push image
    print("\nPushing image to ECR...")
    push_cmd = f"docker push {ECR_URI}:latest"
    result = subprocess.run(push_cmd, shell=True)
    if result.returncode != 0:
        print("✗ Docker push failed")
        sys.exit(1)
    print("✓ Image pushed to ECR")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 3: Create IAM role for App Runner
print("\nStep 3: Creating IAM role for App Runner...")
role_name = 'AppRunnerECRAccessRole-Singapore'

try:
    # Check if role exists
    try:
        role_response = iam.get_role(RoleName=role_name)
        access_role_arn = role_response['Role']['Arn']
        print(f"✓ Using existing IAM role: {access_role_arn}")
    except iam.exceptions.NoSuchEntityException:
        # Create role
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "build.apprunner.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=str(trust_policy).replace("'", '"'),
            Description='Allows App Runner to access ECR in Singapore'
        )
        access_role_arn = role_response['Role']['Arn']
        
        # Attach ECR policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess'
        )
        
        print(f"✓ Created IAM role: {access_role_arn}")
        print("Waiting for role to propagate...")
        time.sleep(10)

except Exception as e:
    print(f"✗ Error creating IAM role: {e}")
    sys.exit(1)

# Step 4: Create App Runner service
print("\nStep 4: Creating App Runner service in Singapore...")

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
            print("SINGAPORE DEPLOYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"\nYour Streamlit UI is live at:")
            print(f"  https://{service_url}")
            print(f"\nService Details:")
            print(f"  Name: {APP_RUNNER_SERVICE_NAME}")
            print(f"  Region: {AWS_REGION} (Singapore)")
            print(f"  ARN: {service_arn}")
            print(f"\nExpected Performance from India:")
            print(f"  Latency: 50-100ms")
            print(f"  Load Time: 2-3 seconds")
            print("\n" + "=" * 60)
            
            # Save URL to file
            with open('SINGAPORE_URL.txt', 'w') as f:
                f.write(f"https://{service_url}")
            print("\n✓ Service URL saved to SINGAPORE_URL.txt")
            
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
