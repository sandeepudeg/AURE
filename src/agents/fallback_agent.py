#!/usr/bin/env python3
"""
Fallback Agent - Direct Bedrock API calls (non-streaming)
Used when Strands SDK streaming fails with "Operation not allowed"
"""

import boto3
import os
import logging
from dotenv import load_dotenv
from config import BEDROCK_MODEL_ID, BEDROCK_REGION

load_dotenv()

logger = logging.getLogger(__name__)

FALLBACK_SYSTEM_PROMPT = """You are Gram-Setu (Village Bridge), an AI assistant for Indian farmers.

You provide direct, helpful answers about:
- Crop diseases and pest management
- Market prices and trends
- Government schemes (PM-Kisan, PMFBY, etc.)
- Irrigation and water management
- Weather-based farming advice
- Best farming practices

GUIDELINES:
- Use simple, farmer-friendly language
- Provide practical, actionable advice
- Suggest low-cost solutions first
- Be specific and direct
- If you need more information, ask clarifying questions

Always respond in a helpful, supportive manner.
"""


def fallback_agent(query: str, system_prompt: str = None) -> str:
    """
    Fallback agent using direct Bedrock API (non-streaming converse)
    
    Args:
        query: User's query
        system_prompt: Custom system prompt (defaults to farm assistant)
    
    Returns:
        Agent response text
    """
    if system_prompt is None:
        system_prompt = FALLBACK_SYSTEM_PROMPT
    
    try:
        # Initialize Bedrock runtime client
        bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=BEDROCK_REGION
        )
        
        logger.info(f"Using fallback agent with model: {BEDROCK_MODEL_ID}")
        
        # Call non-streaming converse API
        response = bedrock_runtime.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{
                'text': system_prompt
            }],
            messages=[{
                'role': 'user',
                'content': [{'text': query}]
            }],
            inferenceConfig={
                'maxTokens': 2000,
                'temperature': 0.7
            }
        )
        
        # Extract response text
        response_text = response['output']['message']['content'][0]['text']
        
        logger.info("Fallback agent response generated successfully")
        return response_text
        
    except Exception as e:
        logger.error(f"Fallback agent error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    print("\n🌾 Fallback Farm Assistant 🌾\n")
    try:
        response = fallback_agent("What are the symptoms of wheat rust disease?")
        print(f"\n{response}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
