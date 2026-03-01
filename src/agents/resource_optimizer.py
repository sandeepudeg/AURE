#!/usr/bin/env python3
"""
Resource-Optimizer Agent - Irrigation & Weather Recommendations
Handles: Evapotranspiration calculation, soil moisture analysis, irrigation scheduling
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

# Initialize MCP Client for Resource-Optimizer
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


# MCP Tool Functions for Resource-Optimizer
def get_current_weather(location: str, units: str = 'metric') -> dict:
    """
    Get current weather conditions via MCP
    
    Args:
        location: Location name (city, district, or coordinates)
        units: Units system ('metric' or 'imperial')
    
    Returns:
        Current weather data
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_current_weather',
            agent_role='Resource-Optimizer',
            params={
                'location': location,
                'units': units
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch current weather for {location}'
        }


def get_weather_forecast(location: str, days: int = 3) -> dict:
    """
    Get weather forecast for next N days via MCP
    
    Args:
        location: Location name (city, district, or coordinates)
        days: Number of days to forecast (1-7)
    
    Returns:
        Weather forecast data
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_weather_forecast',
            agent_role='Resource-Optimizer',
            params={
                'location': location,
                'days': days
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch weather forecast for {location}'
        }


RESOURCE_OPTIMIZER_PROMPT = """You are a Resource Optimization Expert specializing in:
1. Irrigation scheduling and water management
2. Weather-based crop recommendations
3. Evapotranspiration (ET) calculations
4. Soil moisture analysis
5. Pump scheduling optimization

When providing irrigation advice:
- Use get_current_weather tool to check current conditions
- Use get_weather_forecast tool to plan irrigation schedule
- Calculate water requirements based on crop type and weather
- Analyze soil moisture levels from sensor data
- Consider upcoming weather forecasts
- Optimize pump schedules to save electricity costs
- Suggest water conservation techniques

You have access to these tools:
- get_current_weather(location, units): Get current weather conditions
- get_weather_forecast(location, days): Get weather forecast for planning

Always provide practical, cost-effective recommendations for Indian farmers.
Focus on water conservation and electricity cost savings.
"""

resource_optimizer_agent = Agent(
    model=BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        temperature=0.3
    ),
    system_prompt=RESOURCE_OPTIMIZER_PROMPT,
    tools=[get_current_weather, get_weather_forecast]
)

if __name__ == "__main__":
    print("\n💧 Resource-Optimizer Agent 💧\n")
    response = resource_optimizer_agent("What is the weather forecast for Nashik, Maharashtra for the next 3 days? Should I irrigate my wheat field?")
    print(response)
