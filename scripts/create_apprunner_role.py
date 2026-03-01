#!/usr/bin/env python3
"""
Create IAM role for App Runner to access ECR
"""

import boto3
import json

iam = boto3.client('iam')

# Trust policy for App Runner
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "build.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

role_name = "AppRunnerECRAccessRole"

print("Creating IAM role for App Runner...")

try:
    # Create role
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Allows App Runner to access ECR images"
    )
    
    role_arn = response['Role']['Arn']
    print(f"✓ Created role: {role_arn}")
    
    # Attach ECR read-only policy
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
    )
    
    print(f"✓ Attached ECR access policy")
    print(f"\nRole ARN: {role_arn}")
    
except iam.exceptions.EntityAlreadyExistsException:
    # Role already exists, get its ARN
    response = iam.get_role(RoleName=role_name)
    role_arn = response['Role']['Arn']
    print(f"✓ Role already exists: {role_arn}")
    
except Exception as e:
    print(f"✗ Error: {e}")
