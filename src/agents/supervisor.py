#!/usr/bin/env python3
"""
Supervisor Agent - Main Orchestrator
Routes queries to specialist agents (Agri-Expert, Policy-Navigator, Resource-Optimizer)
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

from config import BEDROCK_MODEL_ID

# Import specialist agents
from .agri_expert import agri_expert_agent
from .policy_navigator import policy_navigator_agent
from .resource_optimizer import resource_optimizer_agent

load_dotenv()

SUPERVISOR_PROMPT = """You are Gram-Setu (Village Bridge) AI Orchestrator.

TASK: Analyze farmer queries and route to the appropriate specialist agent.

AVAILABLE AGENTS:
1. agri_expert_agent: Crop diseases, pests, market prices, treatment recommendations
2. policy_navigator_agent: PM-Kisan scheme eligibility, government subsidies, application guidance
3. resource_optimizer_agent: Irrigation scheduling, water management, weather-based recommendations

ROUTING LOGIC:
- IF query contains image OR mentions disease/pest/crop problem → agri_expert_agent
- IF query mentions PM-Kisan/subsidy/scheme/government benefits → policy_navigator_agent
- IF query mentions irrigation/water/weather/pump schedule → resource_optimizer_agent
- IF query is complex (multiple domains) → Invoke multiple agents in sequence

CONSTRAINTS:
- Use simple, non-technical language
- Always suggest lowest-cost option first
- If ambiguous, ask clarifying question
- Provide actionable advice

Always respond in a helpful, farmer-friendly manner.
"""

supervisor_agent = Agent(
    model=BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        temperature=0.3
    ),
    system_prompt=SUPERVISOR_PROMPT,
    tools=[agri_expert_agent, policy_navigator_agent, resource_optimizer_agent]
)

if __name__ == "__main__":
    print("\n🌾 Gram-Setu Supervisor Agent 🌾\n")
    print("Ask any farming question, and I'll route it to the right specialist.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            response = supervisor_agent(user_input)
            print(str(response))
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
