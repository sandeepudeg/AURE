#!/usr/bin/env python3
"""
Simple test script for URE agents
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents import supervisor_agent, agri_expert_agent, policy_navigator_agent, resource_optimizer_agent

def test_individual_agents():
    """Test each specialist agent individually"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL AGENTS")
    print("="*60)
    
    # Test Agri-Expert
    print("\n1. Testing Agri-Expert Agent...")
    print("-" * 60)
    try:
        response = agri_expert_agent("What are the symptoms of tomato blight?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Policy-Navigator
    print("\n2. Testing Policy-Navigator Agent...")
    print("-" * 60)
    try:
        response = policy_navigator_agent("Am I eligible for PM-Kisan if I have 1.5 hectares?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Resource-Optimizer
    print("\n3. Testing Resource-Optimizer Agent...")
    print("-" * 60)
    try:
        response = resource_optimizer_agent("When should I irrigate? Soil moisture is 0.4")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

def test_supervisor():
    """Test supervisor agent routing"""
    print("\n" + "="*60)
    print("TESTING SUPERVISOR AGENT")
    print("="*60)
    
    test_queries = [
        "My wheat has yellow spots",
        "Am I eligible for PM-Kisan?",
        "When should I water my crops?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 60)
        try:
            response = supervisor_agent(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("\n🌾 URE Agent Testing 🌾\n")
    
    # Test individual agents
    test_individual_agents()
    
    # Test supervisor
    test_supervisor()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60 + "\n")
