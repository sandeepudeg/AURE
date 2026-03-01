#!/usr/bin/env python3
"""
Unit Tests for MCP Client
Target: 90% coverage as per TASK-4.3
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp.client import MCPClient
import json


@pytest.fixture
def mock_tool_registry(tmp_path):
    """Create a mock tool registry file"""
    registry = {
        "get_mandi_prices": {
            "tool_id": "get_mandi_prices",
            "server_name": "agmarknet",
            "description": "Get market prices",
            "permissions": ["Agri-Expert", "Supervisor"],
            "timeout_ms": 5000,
            "retry_count": 3
        },
        "get_current_weather": {
            "tool_id": "get_current_weather",
            "server_name": "weather",
            "description": "Get current weather",
            "permissions": ["Resource-Optimizer", "Supervisor"],
            "timeout_ms": 3000,
            "retry_count": 3
        }
    }
    
    registry_file = tmp_path / "tool_registry.json"
    with open(registry_file, 'w') as f:
        json.dump(registry, f)
    
    return str(registry_file)


@pytest.fixture
def mcp_client(mock_tool_registry):
    """Create MCP Client instance"""
    servers = {
        "agmarknet": "http://localhost:8001",
        "weather": "http://localhost:8002"
    }
    return MCPClient(mock_tool_registry, servers)


def test_load_tool_registry(mcp_client):
    """Test tool registry loading"""
    assert len(mcp_client.tool_registry) == 2
    assert "get_mandi_prices" in mcp_client.tool_registry
    assert "get_current_weather" in mcp_client.tool_registry


def test_permission_check_allowed(mcp_client):
    """Test permission check for allowed agent"""
    assert mcp_client._check_permission("get_mandi_prices", "Agri-Expert") == True
    assert mcp_client._check_permission("get_mandi_prices", "Supervisor") == True


def test_permission_check_denied(mcp_client):
    """Test permission check for denied agent"""
    assert mcp_client._check_permission("get_mandi_prices", "Policy-Navigator") == False
    assert mcp_client._check_permission("get_current_weather", "Agri-Expert") == False


def test_permission_check_invalid_tool(mcp_client):
    """Test permission check for non-existent tool"""
    assert mcp_client._check_permission("invalid_tool", "Agri-Expert") == False


@patch('mcp.client.requests.post')
def test_call_tool_success(mock_post, mcp_client):
    """Test successful tool call"""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"price": 50}
    }
    mock_post.return_value = mock_response
    
    result = mcp_client.call_tool(
        tool_id="get_mandi_prices",
        agent_role="Agri-Expert",
        params={"crop": "Tomato", "district": "Nashik", "state": "Maharashtra"}
    )
    
    assert result["success"] == True
    assert "data" in result
    assert mock_post.called


@patch('mcp.client.requests.post')
def test_call_tool_permission_denied(mock_post, mcp_client):
    """Test tool call with permission denied"""
    with pytest.raises(PermissionError):
        mcp_client.call_tool(
            tool_id="get_mandi_prices",
            agent_role="Policy-Navigator",  # Not allowed
            params={"crop": "Tomato"}
        )
    
    # Should not call server if permission denied
    assert not mock_post.called


@patch('mcp.client.requests.post')
def test_call_tool_invalid_tool(mock_post, mcp_client):
    """Test tool call with invalid tool ID"""
    with pytest.raises(ValueError):
        mcp_client.call_tool(
            tool_id="invalid_tool",
            agent_role="Agri-Expert",
            params={}
        )
    
    assert not mock_post.called


@patch('mcp.client.requests.post')
def test_call_tool_retry_logic(mock_post, mcp_client):
    """Test retry logic with exponential backoff"""
    # Mock failures then success
    mock_response_fail = Mock()
    mock_response_fail.raise_for_status.side_effect = Exception("Server error")
    
    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"success": True}
    
    mock_post.side_effect = [
        mock_response_fail,
        mock_response_fail,
        mock_response_success
    ]
    
    result = mcp_client.call_tool(
        tool_id="get_mandi_prices",
        agent_role="Agri-Expert",
        params={"crop": "Tomato"}
    )
    
    assert result["success"] == True
    assert mock_post.call_count == 3  # 2 failures + 1 success


@patch('mcp.client.requests.post')
def test_call_tool_fallback_to_cache(mock_post, mcp_client):
    """Test fallback to cached data when server fails"""
    # First call succeeds and caches result
    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"success": True, "data": "cached"}
    mock_post.return_value = mock_response_success
    
    params = {"crop": "Tomato"}
    result1 = mcp_client.call_tool(
        tool_id="get_mandi_prices",
        agent_role="Agri-Expert",
        params=params
    )
    
    assert result1["success"] == True
    
    # Second call fails, should return cached data
    mock_post.side_effect = Exception("Server down")
    
    result2 = mcp_client.call_tool(
        tool_id="get_mandi_prices",
        agent_role="Agri-Expert",
        params=params
    )
    
    assert result2["success"] == True
    assert result2["_cached"] == True
    assert result2["data"] == "cached"


@patch('mcp.client.requests.post')
def test_call_tool_no_cache_available(mock_post, mcp_client):
    """Test error when server fails and no cache available"""
    mock_post.side_effect = Exception("Server down")
    
    with pytest.raises(RuntimeError):
        mcp_client.call_tool(
            tool_id="get_mandi_prices",
            agent_role="Agri-Expert",
            params={"crop": "Wheat"}
        )


def test_get_available_tools_all(mcp_client):
    """Test getting all available tools"""
    tools = mcp_client.get_available_tools()
    assert len(tools) == 2
    assert "get_mandi_prices" in tools
    assert "get_current_weather" in tools


def test_get_available_tools_filtered(mcp_client):
    """Test getting tools filtered by agent role"""
    agri_tools = mcp_client.get_available_tools("Agri-Expert")
    assert "get_mandi_prices" in agri_tools
    assert "get_current_weather" not in agri_tools
    
    resource_tools = mcp_client.get_available_tools("Resource-Optimizer")
    assert "get_current_weather" in resource_tools
    assert "get_mandi_prices" not in resource_tools
    
    supervisor_tools = mcp_client.get_available_tools("Supervisor")
    assert len(supervisor_tools) == 2  # Supervisor has access to all


def test_get_tool_metadata(mcp_client):
    """Test getting tool metadata"""
    metadata = mcp_client.get_tool_metadata("get_mandi_prices")
    assert metadata is not None
    assert metadata["server_name"] == "agmarknet"
    assert metadata["timeout_ms"] == 5000
    
    invalid_metadata = mcp_client.get_tool_metadata("invalid_tool")
    assert invalid_metadata is None


@patch('mcp.client.requests.post')
def test_logging_on_success(mock_post, mcp_client, caplog):
    """Test that successful calls are logged"""
    import logging
    caplog.set_level(logging.INFO)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_post.return_value = mock_response
    
    mcp_client.call_tool(
        tool_id="get_mandi_prices",
        agent_role="Agri-Expert",
        params={"crop": "Tomato"}
    )
    
    assert "MCP tool call successful" in caplog.text or "get_mandi_prices" in caplog.text


@patch('mcp.client.requests.post')
def test_logging_on_failure(mock_post, mcp_client, caplog):
    """Test that failures are logged"""
    mock_post.side_effect = Exception("Server error")
    
    try:
        mcp_client.call_tool(
            tool_id="get_mandi_prices",
            agent_role="Agri-Expert",
            params={"crop": "Tomato"}
        )
    except RuntimeError:
        pass
    
    assert "MCP tool call failed" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=mcp.client", "--cov-report=term-missing"])
