#!/usr/bin/env python3
"""
Agri-Expert Agent - Crop Disease Diagnosis & Market Prices
Handles: Disease identification, treatment recommendations, market prices
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

from config import BEDROCK_MODEL_ID
from pathlib import Path
import sys

# Add parent directory to path for MCP Client import
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.client import MCPClient

load_dotenv()

# Initialize MCP Client for Agri-Expert
def get_mcp_client():
    """Initialize MCP Client with tool registry and servers"""
    tool_registry_path = os.getenv(
        'MCP_TOOL_REGISTRY_PATH',
        str(Path(__file__).parent.parent / 'mcp' / 'tool_registry.json')
    )
    
    servers = {
        'agmarknet': os.getenv('MCP_AGMARKNET_SERVER_URL', 'http://localhost:8001'),
        'weather': os.getenv('MCP_WEATHER_SERVER_URL', 'http://localhost:8002')
    }
    
    return MCPClient(tool_registry_path, servers)

# Global MCP Client instance
mcp_client = get_mcp_client()


# MCP Tool Functions for Agri-Expert
def get_mandi_prices(crop: str, district: str, state: str) -> dict:
    """
    Get current market prices for a crop from Agmarknet via MCP
    
    Args:
        crop: Crop name (e.g., 'Tomato', 'Wheat')
        district: District name
        state: State name
    
    Returns:
        Market price data
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_mandi_prices',
            agent_role='Agri-Expert',
            params={
                'crop': crop,
                'district': district,
                'state': state
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch market prices for {crop}'
        }


def get_nearby_mandis(district: str, radius_km: int = 50) -> dict:
    """
    Get list of nearby mandis (markets) via MCP
    
    Args:
        district: District name
        radius_km: Search radius in kilometers (default: 50)
    
    Returns:
        List of nearby mandis
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_nearby_mandis',
            agent_role='Agri-Expert',
            params={
                'district': district,
                'radius_km': radius_km
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch nearby mandis for {district}'
        }


AGRI_EXPERT_PROMPT = """You are an Agricultural Expert specializing in:
1. Crop disease identification from images
2. Treatment recommendations for plant diseases
3. Market price information for crops
4. Pest management advice

When analyzing crop issues:
- Identify disease/pest from visual symptoms
- Provide organic and chemical treatment options
- Suggest preventive measures
- Give current market prices for the crop using get_mandi_prices tool
- Suggest nearby markets using get_nearby_mandis tool

You have access to these tools:
- get_mandi_prices(crop, district, state): Get current market prices
- get_nearby_mandis(district, radius_km): Get nearby market locations

Always provide practical, actionable advice for Indian farmers.
"""

agri_expert_agent = Agent(
    model=BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        temperature=0.3
    ),
    system_prompt=AGRI_EXPERT_PROMPT,
    tools=[get_mandi_prices, get_nearby_mandis]
)

if __name__ == "__main__":
    print("\n🌾 Agri-Expert Agent 🌾\n")
    response = agri_expert_agent("What are the current market prices for tomatoes in Nashik, Maharashtra?")
    print(response)
