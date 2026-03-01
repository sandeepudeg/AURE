#!/usr/bin/env python3
"""
Bedrock Knowledge Base Tool
Query government scheme information from Bedrock KB
"""

import os
import boto3
import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockKBTool:
    """Tool for querying Bedrock Knowledge Base"""
    
    def __init__(self, kb_id: Optional[str] = None, region: str = 'us-east-1'):
        """
        Initialize Bedrock KB Tool
        
        Args:
            kb_id: Knowledge Base ID (from environment if not provided)
            region: AWS region
        """
        self.kb_id = kb_id or os.getenv('BEDROCK_KB_ID')
        self.region = region
        self.bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=region
        )
        
        if not self.kb_id:
            raise ValueError("BEDROCK_KB_ID not set in environment")
        
        logger.info(f"Initialized Bedrock KB Tool with KB ID: {self.kb_id}")
    
    def query_schemes(
        self,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query government schemes from Knowledge Base
        
        Args:
            query: Natural language query
            max_results: Maximum number of results to return
            filters: Optional metadata filters
        
        Returns:
            Dictionary with results and citations
        """
        try:
            logger.info(f"Querying KB: {query}")
            
            # Prepare request
            request_params = {
                'knowledgeBaseId': self.kb_id,
                'retrievalQuery': {
                    'text': query
                },
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            }
            
            # Add filters if provided
            if filters:
                request_params['retrievalConfiguration']['vectorSearchConfiguration']['filter'] = filters
            
            # Query Knowledge Base
            response = self.bedrock_agent_runtime.retrieve(**request_params)
            
            # Extract results
            results = []
            for item in response.get('retrievalResults', []):
                result = {
                    'content': item.get('content', {}).get('text', ''),
                    'score': item.get('score', 0.0),
                    'location': item.get('location', {}),
                    'metadata': item.get('metadata', {})
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} results")
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
        
        except ClientError as e:
            logger.error(f"KB query failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': []
            }
    
    def query_with_generation(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query KB and generate response using RAG
        
        Args:
            query: Natural language query
            max_results: Maximum number of results for retrieval
        
        Returns:
            Dictionary with generated response and citations
        """
        try:
            logger.info(f"Querying KB with generation: {query}")
            
            # Use RetrieveAndGenerate API
            response = self.bedrock_agent_runtime.retrieve_and_generate(
                input={
                    'text': query
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.kb_id,
                        'modelArn': f'arn:aws:bedrock:{self.region}::foundation-model/amazon.nova-pro-v1:0',
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': max_results
                            }
                        }
                    }
                }
            )
            
            # Extract generated response
            output = response.get('output', {})
            generated_text = output.get('text', '')
            
            # Extract citations
            citations = []
            for citation in response.get('citations', []):
                for reference in citation.get('retrievedReferences', []):
                    citations.append({
                        'content': reference.get('content', {}).get('text', ''),
                        'location': reference.get('location', {}),
                        'metadata': reference.get('metadata', {})
                    })
            
            logger.info(f"Generated response with {len(citations)} citations")
            
            return {
                'success': True,
                'query': query,
                'response': generated_text,
                'citations': citations,
                'session_id': response.get('sessionId')
            }
        
        except ClientError as e:
            logger.error(f"KB generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'response': ''
            }
    
    def get_scheme_details(self, scheme_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific scheme
        
        Args:
            scheme_name: Name of the scheme (e.g., "PM-Kisan")
        
        Returns:
            Scheme details
        """
        query = f"Provide complete details about {scheme_name} scheme including eligibility criteria, benefits, and application process"
        return self.query_with_generation(query, max_results=3)
    
    def check_eligibility(
        self,
        scheme_name: str,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if user is eligible for a scheme
        
        Args:
            scheme_name: Name of the scheme
            user_profile: User profile with land size, location, crops, etc.
        
        Returns:
            Eligibility assessment
        """
        # Build query with user context
        query = f"""Check eligibility for {scheme_name} scheme for a farmer with:
- Land size: {user_profile.get('land_size', 'unknown')} hectares
- Location: {user_profile.get('location', 'unknown')}
- Crops: {', '.join(user_profile.get('crops', []))}
- Category: {user_profile.get('category', 'general')}

Provide clear yes/no answer with explanation."""
        
        return self.query_with_generation(query, max_results=2)


# Singleton instance
_kb_tool_instance = None


def get_kb_tool() -> BedrockKBTool:
    """Get singleton instance of KB tool"""
    global _kb_tool_instance
    if _kb_tool_instance is None:
        _kb_tool_instance = BedrockKBTool()
    return _kb_tool_instance


if __name__ == "__main__":
    # Test the tool
    from dotenv import load_dotenv
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    tool = get_kb_tool()
    
    # Test query
    result = tool.get_scheme_details("PMKSY irrigation scheme")
    print("\n" + "=" * 60)
    print("SCHEME DETAILS - PMKSY")
    print("=" * 60)
    print(result.get('response', 'No response'))
    
    print("\n" + "=" * 60)
    print("CITATIONS")
    print("=" * 60)
    for idx, citation in enumerate(result.get('citations', [])[:2], 1):
        print(f"\n{idx}. {citation.get('content', '')[:200]}...")

