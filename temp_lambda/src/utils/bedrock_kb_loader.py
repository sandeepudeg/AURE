#!/usr/bin/env python3
"""
Bedrock Knowledge Base Loader
Creates and configures Bedrock Knowledge Base for PM-Kisan scheme
Based on AWS Workshop reference implementation
"""

import boto3
import logging
import time
import json
from typing import Optional, Dict, Any, List, Tuple
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, RequestError

logger = logging.getLogger(__name__)


def interactive_sleep(seconds: int):
    """Sleep with progress indicator"""
    dots = ''
    for i in range(seconds):
        dots += '.'
        print(dots, end='\r')
        time.sleep(1)
    print()  # New line after dots


class BedrockKBLoader:
    """Create and configure Bedrock Knowledge Base for URE MVP"""
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize Bedrock KB Loader
        
        Args:
            region: AWS region (Bedrock KB available in us-east-1, us-west-2)
        """
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam')
        self.aoss_client = boto3.client('opensearchserverless', region_name=region)
        
        sts = boto3.client('sts')
        self.account_number = sts.get_caller_identity().get('Account')
        self.identity = sts.get_caller_identity()['Arn']
        
        logger.info(f"Bedrock KB Loader initialized for region: {region}")
    
    def create_bedrock_execution_role(
        self,
        bucket_name: str,
        collection_arn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Knowledge Base Execution IAM Role with all required policies.
        Based on AWS Workshop reference implementation.
        
        Args:
            bucket_name: S3 bucket name for documents
            collection_arn: OpenSearch Serverless collection ARN
        
        Returns:
            IAM role details
        """
        role_name = f'BedrockKBRole-{self.region}-{self.account_number}'
        
        # Define assume role policy
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        # Create the role
        try:
            bedrock_kb_execution_role = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                Description='Amazon Bedrock Knowledge Base Execution Role',
                MaxSessionDuration=3600
            )
            logger.info(f"Created IAM role: {bedrock_kb_execution_role['Role']['RoleName']}")
            time.sleep(10)  # Wait for role to be created
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            bedrock_kb_execution_role = self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Using existing IAM role: {role_name}")
        
        # Define policies to create
        policies: List[Tuple[str, dict, str]] = []
        
        # 1. Foundation Model Policy
        fm_policy_name = f'BedrockKBFMPolicy-{self.region}-{self.account_number}'
        fm_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "BedrockInvokeModelStatement",
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel"],
                    "Resource": [
                        f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1",
                        f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0"
                    ]
                }
            ]
        }
        policies.append((fm_policy_name, fm_policy_document, 'Policy for accessing foundation model'))
        
        # 2. S3 Access Policy
        s3_policy_name = f'BedrockKBS3Policy-{self.region}-{self.account_number}'
        s3_policy_document = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "StringEquals": {
                        "aws:ResourceAccount": f"{self.account_number}"
                    }
                }
            }]
        }
        policies.append((s3_policy_name, s3_policy_document, 'Policy for reading documents from S3'))
        
        # 3. OpenSearch Serverless Policy (if collection ARN provided)
        if collection_arn:
            collection_id = collection_arn.split('/')[-1]
            oss_policy_name = f'BedrockKBOSSPolicy-{self.region}-{self.account_number}'
            oss_policy_document = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": ["aoss:APIAccessAll"],
                    "Resource": [collection_arn]
                }]
            }
            policies.append((oss_policy_name, oss_policy_document, 'Policy for accessing OpenSearch Serverless'))
        
        # Create and attach all policies
        for policy_name, policy_document, description in policies:
            try:
                policy = self.iam_client.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(policy_document),
                    Description=description
                )
                policy_arn = policy['Policy']['Arn']
                logger.info(f"Created policy: {policy_name}")
            except self.iam_client.exceptions.EntityAlreadyExistsException:
                policy_arn = f"arn:aws:iam::{self.account_number}:policy/{policy_name}"
                logger.info(f"Using existing policy: {policy_name}")
            
            # Attach policy to role
            try:
                self.iam_client.attach_role_policy(
                    RoleName=bedrock_kb_execution_role['Role']['RoleName'],
                    PolicyArn=policy_arn
                )
                logger.info(f"Attached policy {policy_name} to role")
            except Exception as e:
                logger.warning(f"Could not attach policy {policy_name}: {e}")
        
        return bedrock_kb_execution_role
    
    def create_policies_in_oss(self, collection_name: str, bedrock_role_arn: str):
        """
        Create OpenSearch Serverless security policies
        
        Args:
            collection_name: Collection name
            bedrock_role_arn: Bedrock execution role ARN
        """
        encryption_policy_name = f'{collection_name}-encryption'
        network_policy_name = f'{collection_name}-network'
        access_policy_name = f'{collection_name}-data'
        
        # Create encryption policy
        try:
            self.aoss_client.create_security_policy(
                name=encryption_policy_name,
                type='encryption',
                policy=json.dumps({
                    'Rules': [{'Resource': ['collection/' + collection_name],
                               'ResourceType': 'collection'}],
                    'AWSOwnedKey': True
                })
            )
            logger.info(f"Created encryption policy: {encryption_policy_name}")
        except self.aoss_client.exceptions.ConflictException:
            logger.info(f"Encryption policy {encryption_policy_name} already exists")
        
        # Create network policy
        try:
            self.aoss_client.create_security_policy(
                name=network_policy_name,
                type='network',
                policy=json.dumps([
                    {'Rules': [{'Resource': ['collection/' + collection_name],
                                'ResourceType': 'collection'}],
                     'AllowFromPublic': True}
                ])
            )
            logger.info(f"Created network policy: {network_policy_name}")
        except self.aoss_client.exceptions.ConflictException:
            logger.info(f"Network policy {network_policy_name} already exists")
        
        # Create data access policy
        try:
            self.aoss_client.create_access_policy(
                name=access_policy_name,
                type='data',
                policy=json.dumps([
                    {
                        'Rules': [
                            {
                                'Resource': ['collection/' + collection_name],
                                'Permission': [
                                    'aoss:CreateCollectionItems',
                                    'aoss:DeleteCollectionItems',
                                    'aoss:UpdateCollectionItems',
                                    'aoss:DescribeCollectionItems'],
                                'ResourceType': 'collection'
                            },
                            {
                                'Resource': ['index/' + collection_name + '/*'],
                                'Permission': [
                                    'aoss:CreateIndex',
                                    'aoss:DeleteIndex',
                                    'aoss:UpdateIndex',
                                    'aoss:DescribeIndex',
                                    'aoss:ReadDocument',
                                    'aoss:WriteDocument'],
                                'ResourceType': 'index'
                            }],
                        'Principal': [self.identity, bedrock_role_arn],
                        'Description': 'Data access policy for Bedrock KB'}
                ])
            )
            logger.info(f"Created data access policy: {access_policy_name}")
        except self.aoss_client.exceptions.ConflictException:
            logger.info(f"Data access policy {access_policy_name} already exists")
    
    def create_opensearch_collection(
        self,
        collection_name: str = 'ure-knowledge-base'
    ) -> Optional[str]:
        """
        Create OpenSearch Serverless collection
        
        Args:
            collection_name: Collection name
        
        Returns:
            Collection ARN or None
        """
        try:
            collection = self.aoss_client.create_collection(
                name=collection_name,
                type='VECTORSEARCH'
            )
            collection_arn = collection['createCollectionDetail']['arn']
            logger.info(f"OpenSearch collection created: {collection_arn}")
        except self.aoss_client.exceptions.ConflictException:
            collection = self.aoss_client.batch_get_collection(names=[collection_name])['collectionDetails'][0]
            collection_arn = collection['arn']
            logger.info(f"Collection {collection_name} already exists")
        
        # Wait for collection to be active
        logger.info("Waiting for collection to be active...")
        response = self.aoss_client.batch_get_collection(names=[collection_name])
        while (response['collectionDetails'][0]['status']) == 'CREATING':
            print('Creating collection...')
            interactive_sleep(30)
            response = self.aoss_client.batch_get_collection(names=[collection_name])
        
        logger.info('Collection successfully created')
        return collection_arn
    
    def create_vector_index(
        self,
        collection_endpoint: str,
        index_name: str = 'ure-kb-index',
        embedding_dimension: int = 1024
    ):
        """
        Create OpenSearch Serverless vector index
        
        Args:
            collection_endpoint: OpenSearch collection endpoint
            index_name: Index name
            embedding_dimension: Embedding vector dimension (1024 for titan-embed-text-v2)
        """
        # Get AWS credentials for OpenSearch authentication
        credentials = boto3.Session().get_credentials()
        awsauth = AWSV4SignerAuth(credentials, self.region, 'aoss')
        
        # Create OpenSearch client
        oss_client = OpenSearch(
            hosts=[{'host': collection_endpoint, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=300
        )
        
        # Define index body with vector field mapping
        body_json = {
            "settings": {
                "index.knn": "true",
                "number_of_shards": 1,
                "knn.algo_param.ef_search": 512,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "vector": {
                        "type": "knn_vector",
                        "dimension": embedding_dimension,
                        "method": {
                            "name": "hnsw",
                            "engine": "faiss",
                            "space_type": "l2"
                        },
                    },
                    "text": {
                        "type": "text"
                    },
                    "text-metadata": {
                        "type": "text"
                    }
                }
            }
        }
        
        try:
            response = oss_client.indices.create(index=index_name, body=json.dumps(body_json))
            logger.info(f'Created vector index: {index_name}')
            logger.info(f'Index response: {response}')
            interactive_sleep(60)  # Wait for index to be ready
        except RequestError as e:
            if 'resource_already_exists_exception' in str(e.error).lower():
                logger.info(f'Vector index {index_name} already exists')
            else:
                logger.error(f'Error creating index: {e.error}')
                raise
    
    def create_knowledge_base(
        self,
        kb_name: str = 'ure-pm-kisan-kb',
        s3_bucket: str = 'knowledge-base-bharat',
        s3_prefix: str = 'schemes/',
        opensearch_collection_arn: Optional[str] = None
    ) -> Optional[str]:
        """
        Create Bedrock Knowledge Base with proper IAM setup
        
        Args:
            kb_name: Knowledge Base name
            s3_bucket: S3 bucket containing documents
            s3_prefix: S3 prefix for documents
            opensearch_collection_arn: OpenSearch collection ARN
        
        Returns:
            Knowledge Base ID or None
        """
        try:
            # Create IAM role with all policies
            logger.info("Creating Bedrock execution role...")
            bedrock_kb_execution_role = self.create_bedrock_execution_role(
                bucket_name=s3_bucket,
                collection_arn=opensearch_collection_arn
            )
            
            # Wait for IAM changes to propagate
            logger.info("Waiting for IAM changes to propagate...")
            interactive_sleep(20)
            
            # Create Knowledge Base
            kb_config = {
                'name': kb_name,
                'description': 'PM-Kisan scheme information for URE MVP',
                'roleArn': bedrock_kb_execution_role['Role']['Arn'],
                'knowledgeBaseConfiguration': {
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0'
                    }
                }
            }
            
            if opensearch_collection_arn:
                kb_config['storageConfiguration'] = {
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': opensearch_collection_arn,
                        'vectorIndexName': 'ure-kb-index',
                        'fieldMapping': {
                            'vectorField': 'vector',
                            'textField': 'text',
                            'metadataField': 'text-metadata'
                        }
                    }
                }
            
            response = self.bedrock_agent.create_knowledge_base(**kb_config)
            kb_id = response['knowledgeBase']['knowledgeBaseId']
            
            logger.info(f"Knowledge Base created: {kb_id}")
            return kb_id
        
        except ClientError as e:
            logger.error(f"Failed to create Knowledge Base: {e}")
            return None
    
    def configure_s3_bucket_policy(self, bucket_name: str, bedrock_role_arn: str):
        """
        Configure S3 bucket policy to allow Bedrock access from any region
        
        Args:
            bucket_name: S3 bucket name
            bedrock_role_arn: Bedrock execution role ARN
        """
        try:
            # Get bucket location to use correct regional client
            s3_global = boto3.client('s3')
            bucket_location = s3_global.get_bucket_location(Bucket=bucket_name)
            bucket_region = bucket_location['LocationConstraint'] or 'us-east-1'
            
            # Create S3 client for bucket's region
            s3_bucket_client = boto3.client('s3', region_name=bucket_region)
            logger.info(f"Bucket {bucket_name} is in region: {bucket_region}")
            
            # Get existing bucket policy if any
            try:
                response = s3_bucket_client.get_bucket_policy(Bucket=bucket_name)
                existing_policy = json.loads(response['Policy'])
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    existing_policy = {"Version": "2012-10-17", "Statement": []}
                else:
                    raise
            
            # Add Bedrock access statement
            bedrock_statement = {
                "Sid": "AllowBedrockKnowledgeBaseAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": bedrock_role_arn
                },
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }
            
            # Check if statement already exists
            statement_exists = False
            for stmt in existing_policy['Statement']:
                if stmt.get('Sid') == 'AllowBedrockKnowledgeBaseAccess':
                    statement_exists = True
                    break
            
            if not statement_exists:
                existing_policy['Statement'].append(bedrock_statement)
                
                # Update bucket policy
                s3_bucket_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(existing_policy)
                )
                logger.info(f"✓ Updated S3 bucket policy for {bucket_name}")
                logger.info(f"  Added cross-region access for Bedrock role")
            else:
                logger.info(f"✓ S3 bucket policy already configured for {bucket_name}")
        
        except ClientError as e:
            logger.error(f"Failed to configure S3 bucket policy: {e}")
            raise
    
    def create_data_source(
        self,
        kb_id: str,
        s3_bucket: str = 'knowledge-base-bharat',
        s3_prefix: str = 'schemes/',
        data_source_name: str = 'pm-kisan-docs'
    ) -> Optional[str]:
        """
        Create data source for Knowledge Base
        
        Args:
            kb_id: Knowledge Base ID
            s3_bucket: S3 bucket name
            s3_prefix: S3 prefix
            data_source_name: Data source name
        
        Returns:
            Data source ID or None
        """
        try:
            response = self.bedrock_agent.create_data_source(
                knowledgeBaseId=kb_id,
                name=data_source_name,
                description='PM-Kisan scheme PDFs and documents',
                dataSourceConfiguration={
                    'type': 'S3',
                    's3Configuration': {
                        'bucketArn': f'arn:aws:s3:::{s3_bucket}',
                        'inclusionPrefixes': [s3_prefix]
                    }
                }
            )
            
            data_source_id = response['dataSource']['dataSourceId']
            logger.info(f"Data source created: {data_source_id}")
            return data_source_id
        
        except ClientError as e:
            logger.error(f"Failed to create data source: {e}")
            return None
    
    def start_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str
    ) -> Optional[str]:
        """
        Start ingestion job to index documents
        
        Args:
            kb_id: Knowledge Base ID
            data_source_id: Data source ID
        
        Returns:
            Ingestion job ID or None
        """
        try:
            response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id
            )
            
            job_id = response['ingestionJob']['ingestionJobId']
            logger.info(f"Ingestion job started: {job_id}")
            
            # Monitor job status
            self._monitor_ingestion_job(kb_id, data_source_id, job_id)
            
            return job_id
        
        except ClientError as e:
            logger.error(f"Failed to start ingestion job: {e}")
            return None
    
    def _monitor_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str,
        job_id: str,
        max_wait: int = 600
    ):
        """Monitor ingestion job status"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=job_id
                )
                
                status = response['ingestionJob']['status']
                logger.info(f"Ingestion job status: {status}")
                
                if status == 'COMPLETE':
                    logger.info("Ingestion job completed successfully")
                    return
                elif status == 'FAILED':
                    logger.error("Ingestion job failed")
                    return
                
                time.sleep(30)
            
            except ClientError as e:
                logger.error(f"Failed to get ingestion job status: {e}")
                return
        
        logger.warning("Ingestion job monitoring timed out")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize loader
    loader = BedrockKBLoader()
    
    print("\nBedrock Knowledge Base Loader")
    print("=" * 50)
    print("\nSteps to create Knowledge Base:")
    print("1. Create OpenSearch Serverless collection")
    print("2. Create IAM role and policies")
    print("3. Create Knowledge Base")
    print("4. Create data source (S3)")
    print("5. Start ingestion job")
    
    print("\nNote: Ensure S3 bucket has PM-Kisan PDFs uploaded first!")
