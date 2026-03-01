#!/usr/bin/env python3
"""
Agent Configuration
Centralized configuration for all URE agents
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bedrock Model Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")

# Agent Temperature Settings
SUPERVISOR_TEMPERATURE = 0.3  # Balanced for routing decisions
AGRI_EXPERT_TEMPERATURE = 0.3  # Precise for disease identification
POLICY_NAVIGATOR_TEMPERATURE = 0.2  # Very precise for eligibility rules
RESOURCE_OPTIMIZER_TEMPERATURE = 0.3  # Balanced for recommendations

# MCP Server Configuration
MCP_AGMARKNET_SERVER_URL = os.getenv("MCP_AGMARKNET_SERVER_URL", "https://agmarknet-mcp-server.com")
MCP_WEATHER_SERVER_URL = os.getenv("MCP_WEATHER_SERVER_URL", "https://weather-mcp-server.com")

# Tool Registry Path
MCP_TOOL_REGISTRY_PATH = os.getenv("MCP_TOOL_REGISTRY_PATH", "src/mcp/tool_registry.json")

# Agent Role Names (for MCP permissions)
ROLE_SUPERVISOR = "Supervisor"
ROLE_AGRI_EXPERT = "Agri-Expert"
ROLE_POLICY_NAVIGATOR = "Policy-Navigator"
ROLE_RESOURCE_OPTIMIZER = "Resource-Optimizer"

# AWS Service Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "ure-conversations")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "knowledge-base-bharat")
BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID", "")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CLOUDWATCH_LOG_GROUP = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/lambda/ure-mvp")

# Performance Settings
MAX_CONVERSATION_HISTORY = 10  # Last N messages to keep
RESPONSE_TIMEOUT_SECONDS = 30
MCP_TOOL_TIMEOUT_MS = 5000
MCP_RETRY_COUNT = 3

# Language Support
SUPPORTED_LANGUAGES = ["english", "hindi", "marathi"]
DEFAULT_LANGUAGE = "english"

# Agent Configuration Dictionary
AGENT_CONFIG = {
    "supervisor": {
        "model_id": BEDROCK_MODEL_ID,
        "temperature": SUPERVISOR_TEMPERATURE,
        "role": ROLE_SUPERVISOR,
        "max_tokens": 2000
    },
    "agri_expert": {
        "model_id": BEDROCK_MODEL_ID,
        "temperature": AGRI_EXPERT_TEMPERATURE,
        "role": ROLE_AGRI_EXPERT,
        "max_tokens": 2000
    },
    "policy_navigator": {
        "model_id": BEDROCK_MODEL_ID,
        "temperature": POLICY_NAVIGATOR_TEMPERATURE,
        "role": ROLE_POLICY_NAVIGATOR,
        "max_tokens": 2000
    },
    "resource_optimizer": {
        "model_id": BEDROCK_MODEL_ID,
        "temperature": RESOURCE_OPTIMIZER_TEMPERATURE,
        "role": ROLE_RESOURCE_OPTIMIZER,
        "max_tokens": 2000
    }
}

# MCP Server Configuration
MCP_SERVERS = {
    "agmarknet": {
        "url": MCP_AGMARKNET_SERVER_URL,
        "timeout_ms": MCP_TOOL_TIMEOUT_MS,
        "retry_count": MCP_RETRY_COUNT
    },
    "weather": {
        "url": MCP_WEATHER_SERVER_URL,
        "timeout_ms": MCP_TOOL_TIMEOUT_MS,
        "retry_count": MCP_RETRY_COUNT
    }
}
