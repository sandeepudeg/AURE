#!/usr/bin/env python3
"""
Simple Supervisor Agent - Direct responses without delegation
For local testing and faster responses
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

load_dotenv()

SIMPLE_SUPERVISOR_PROMPT = """You are Gram-Setu (Village Bridge), an AI assistant for Indian farmers.

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

supervisor_simple_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
        temperature=0.7
    ),
    system_prompt=SIMPLE_SUPERVISOR_PROMPT
)

if __name__ == "__main__":
    print("\n🌾 Gram-Setu AI Assistant 🌾\n")
    print("Ask any farming question!")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            response = supervisor_simple_agent(user_input)
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
