#!/usr/bin/env python3
"""
Conversation example for the Vertex Search Agent.

This example demonstrates how to:
1. Start a conversation
2. Add context
3. Ask follow-up questions
4. Maintain conversation history
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
    """Main function demonstrating conversation usage."""
    
    # Initialize the agent
    agent = VertexSearchAgent(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        search_engine_id=os.getenv("VERTEX_SEARCH_ENGINE_ID")
    )
    
    # Start a conversation
    conversation = agent.start_conversation("tech_discussion")
    
    print("🤖 Vertex Search Agent - Conversation Example")
    print("=" * 50)
    
    # Add some context to the conversation
    conversation.add_context("Focus on recent developments from 2024")
    print("📝 Added context: Focus on recent developments from 2024")
    
    # Conversation flow
    conversation_flow = [
        "What are the latest developments in AI?",
        "How do these compare to developments from 2023?",
        "What are the main challenges in AI development?",
        "Which companies are leading in AI research?",
        "What are the ethical considerations in AI?"
    ]
    
    for i, question in enumerate(conversation_flow, 1):
        print(f"\n📝 Question {i}: {question}")
        print("-" * 40)
        
        try:
            # Ask the question in the conversation context
            response = await conversation.ask(question)
            print(f"🤖 Response: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Add a small delay between questions
        await asyncio.sleep(1)
    
    # Display conversation history
    print("\n📚 Conversation History:")
    print("=" * 30)
    history = conversation.get_history()
    for i, message in enumerate(history, 1):
        print(f"{i}. {message.role.upper()}: {message.content[:100]}...")
        if message.search_results:
            print(f"   📊 Found {len(message.search_results)} search results")
    
    # List all active conversations
    print(f"\n🔄 Active conversations: {agent.list_conversations()}")
    
    # End the conversation
    agent.end_conversation("tech_discussion")
    print("✅ Conversation ended")
    
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 