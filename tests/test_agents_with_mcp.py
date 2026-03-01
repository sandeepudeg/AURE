#!/usr/bin/env python3
"""
Test Agents with MCP Client Integration
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)


def test_agri_expert_with_mcp():
    """Test Agri-Expert agent with MCP tools"""
    print("\n" + "=" * 60)
    print("TEST: Agri-Expert with MCP Tools")
    print("=" * 60)
    
    from agents.agri_expert import agri_expert_agent
    
    query = "What are the current market prices for tomatoes in Nashik, Maharashtra?"
    print(f"\nQuery: {query}")
    
    try:
        response = agri_expert_agent(query)
        print(f"\nResponse: {str(response)[:500]}...")
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False


def test_resource_optimizer_with_mcp():
    """Test Resource-Optimizer agent with MCP tools"""
    print("\n" + "=" * 60)
    print("TEST: Resource-Optimizer with MCP Tools")
    print("=" * 60)
    
    from agents.resource_optimizer import resource_optimizer_agent
    
    query = "What is the weather forecast for Nashik for the next 3 days? Should I irrigate my wheat field?"
    print(f"\nQuery: {query}")
    
    try:
        response = resource_optimizer_agent(query)
        print(f"\nResponse: {str(response)[:500]}...")
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False


def test_mcp_tool_permissions():
    """Test MCP tool permission enforcement"""
    print("\n" + "=" * 60)
    print("TEST: MCP Tool Permission Enforcement")
    print("=" * 60)
    
    from mcp.client import MCPClient
    
    tool_registry_path = "src/mcp/tool_registry.json"
    servers = {
        'agmarknet': 'http://localhost:8001',
        'weather': 'http://localhost:8002'
    }
    
    client = MCPClient(tool_registry_path, servers)
    
    # Test 1: Agri-Expert should access get_mandi_prices
    print("\n1. Agri-Expert accessing get_mandi_prices (should succeed)")
    try:
        result = client.call_tool(
            tool_id='get_mandi_prices',
            agent_role='Agri-Expert',
            params={'crop': 'Tomato', 'district': 'Nashik', 'state': 'Maharashtra'}
        )
        print(f"✓ Success: {result.get('success', False)}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Policy-Navigator should NOT access get_mandi_prices
    print("\n2. Policy-Navigator accessing get_mandi_prices (should fail)")
    try:
        result = client.call_tool(
            tool_id='get_mandi_prices',
            agent_role='Policy-Navigator',
            params={'crop': 'Tomato', 'district': 'Nashik', 'state': 'Maharashtra'}
        )
        print(f"✗ Should have been denied but succeeded")
        return False
    except PermissionError as e:
        print(f"✓ Correctly denied: {e}")
    
    # Test 3: Resource-Optimizer should access get_current_weather
    print("\n3. Resource-Optimizer accessing get_current_weather (should succeed)")
    try:
        result = client.call_tool(
            tool_id='get_current_weather',
            agent_role='Resource-Optimizer',
            params={'location': 'Nashik, Maharashtra'}
        )
        print(f"✓ Success: {result.get('success', False)}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 4: Agri-Expert should NOT access get_current_weather
    print("\n4. Agri-Expert accessing get_current_weather (should fail)")
    try:
        result = client.call_tool(
            tool_id='get_current_weather',
            agent_role='Agri-Expert',
            params={'location': 'Nashik, Maharashtra'}
        )
        print(f"✗ Should have been denied but succeeded")
        return False
    except PermissionError as e:
        print(f"✓ Correctly denied: {e}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AGENTS WITH MCP CLIENT INTEGRATION TEST")
    print("=" * 60)
    print("\nNOTE: MCP servers must be running on ports 8001 and 8002")
    print("Start them with: py scripts/run_mcp_servers.py\n")
    
    tests = [
        ("MCP Tool Permissions", test_mcp_tool_permissions),
        ("Agri-Expert with MCP", test_agri_expert_with_mcp),
        ("Resource-Optimizer with MCP", test_resource_optimizer_with_mcp)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} passed")
            else:
                failed += 1
                print(f"\n✗ {test_name} failed")
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - MCP Integration Complete!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
