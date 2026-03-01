#!/usr/bin/env python3
"""
Local testing script for URE agents
Tests agents without AWS deployment
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.supervisor import supervisor_agent
from agents.agri_expert import agri_expert_agent
from agents.policy_navigator import policy_navigator_agent
from agents.resource_optimizer import resource_optimizer_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_supervisor_routing():
    """Test Supervisor Agent query routing"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Supervisor Agent Routing")
    logger.info("=" * 60)
    
    test_queries = [
        "What disease is affecting my tomato plant?",
        "Am I eligible for PM-Kisan scheme?",
        "How much water should I use for irrigation today?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        try:
            response = supervisor_agent(query)
            logger.info(f"Response: {str(response)[:200]}...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


def test_agri_expert():
    """Test Agri-Expert Agent"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Agri-Expert Agent")
    logger.info("=" * 60)
    
    test_queries = [
        "What are the symptoms of tomato late blight?",
        "How do I treat powdery mildew on grapes?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        try:
            response = agri_expert_agent(query)
            logger.info(f"Response: {str(response)[:200]}...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


def test_policy_navigator():
    """Test Policy-Navigator Agent"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Policy-Navigator Agent")
    logger.info("=" * 60)
    
    test_queries = [
        "What is PM-Kisan scheme?",
        "Am I eligible for PMKSY irrigation scheme?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        try:
            response = policy_navigator_agent(query)
            logger.info(f"Response: {str(response)[:200]}...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


def test_resource_optimizer():
    """Test Resource-Optimizer Agent"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Resource-Optimizer Agent")
    logger.info("=" * 60)
    
    test_queries = [
        "How much water should I use for my wheat crop today?",
        "Should I irrigate my field today?"
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        try:
            response = resource_optimizer_agent(query)
            logger.info(f"Response: {str(response)[:200]}...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("URE AGENT LOCAL TESTING")
    logger.info("=" * 60)
    
    try:
        test_supervisor_routing()
        test_agri_expert()
        test_policy_navigator()
        test_resource_optimizer()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS COMPLETED")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"\n✗ Testing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
