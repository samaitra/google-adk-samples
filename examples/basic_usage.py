#!/usr/bin/env python3
"""
Basic usage example for the Vertex Search Agent.

This example demonstrates how to:
1. Initialize the agent
2. Ask a simple question
3. Get a grounded response
"""

import asyncio
import os
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import VertexSearchAgent

# Load environment variables
load_dotenv()


async def main():
    """Main function demonstrating basic agent usage."""
    
    # Initialize the agent
    agent = VertexSearchAgent(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        search_engine_id=os.getenv("VERTEX_SEARCH_ENGINE_ID")
    )
    
    # Example questions to ask
    questions = [
        "What are the latest developments in artificial intelligence?",
        "How does machine learning work?",
        "What are the benefits of cloud computing?",
        "What is the current state of renewable energy?"
    ]
    
    print("🤖 Vertex Search Agent - Basic Usage Example")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 30)
        
        try:
            # Ask the question
            response = await agent.ask(question)
            print(f"🤖 Response: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Add a small delay between questions
        await asyncio.sleep(1)
    
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 