#!/usr/bin/env python3
"""
Command-line interface for the Google ADK with Vertex Search grounding.

This module provides a CLI for interacting with the Vertex Search Agent
directly from the command line.
"""

import asyncio
import argparse
import sys
import os
from typing import Optional
from pathlib import Path

# Add the current directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import VertexSearchAgent, create_agent
from config import load_config, create_config_template


class VertexSearchCLI:
    """Command-line interface for the Vertex Search Agent."""
    
    def __init__(self):
        self.agent: Optional[VertexSearchAgent] = None
        self.conversation = None
    
    async def initialize_agent(self, config_path: Optional[str] = None):
        """Initialize the agent with configuration."""
        try:
            if config_path:
                config = load_config(config_path)
                self.agent = VertexSearchAgent(config=config)
            else:
                self.agent = await create_agent()
            
            print("✅ Agent initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            print("\nPlease ensure you have:")
            print("1. Set up Google Cloud credentials")
            print("2. Configured environment variables (see env.example)")
            print("3. Enabled Vertex Search API in your project")
            sys.exit(1)
    
    async def interactive_mode(self):
        """Run the agent in interactive mode."""
        if not self.agent:
            await self.initialize_agent()
        
        print("\n🤖 Vertex Search Agent - Interactive Mode")
        print("=" * 50)
        print("Type 'help' for commands, 'quit' to exit")
        print("Type 'conversation' to start a multi-turn conversation")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'conversation':
                    await self.conversation_mode()
                
                elif user_input.lower() == 'search':
                    await self.search_mode()
                
                elif user_input.lower() == 'config':
                    self.show_config()
                
                else:
                    # Treat as a question
                    print("🤖 Thinking...")
                    response = await self.agent.ask(user_input)
                    print(f"🤖 Agent: {response}")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def conversation_mode(self):
        """Run the agent in conversation mode."""
        if not self.agent:
            await self.initialize_agent()
        
        conversation = self.agent.start_conversation("cli_conversation")
        
        print("\n💬 Conversation Mode")
        print("=" * 30)
        print("Type 'context <text>' to add context")
        print("Type 'history' to see conversation history")
        print("Type 'back' to return to main mode")
        print("-" * 30)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'back':
                    break
                
                elif user_input.lower() == 'history':
                    self.show_conversation_history(conversation)
                
                elif user_input.lower().startswith('context '):
                    context = user_input[8:]  # Remove 'context ' prefix
                    conversation.add_context(context)
                    print(f"📝 Context added: {context}")
                
                else:
                    # Treat as a question
                    print("🤖 Thinking...")
                    response = await conversation.ask(user_input)
                    print(f"🤖 Agent: {response}")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def search_mode(self):
        """Run the agent in search mode to see raw results."""
        if not self.agent:
            await self.initialize_agent()
        
        print("\n🔍 Search Mode")
        print("=" * 20)
        print("Enter search queries to see raw results")
        print("Type 'back' to return to main mode")
        print("-" * 20)
        
        while True:
            try:
                query = input("\n🔍 Search: ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'back':
                    break
                
                print("🔍 Searching...")
                results = await self.agent.search(query)
                
                if results:
                    print(f"\n📊 Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result.title}")
                        print(f"   Score: {result.score:.3f}")
                        print(f"   {result.snippet[:150]}...")
                        if result.url:
                            print(f"   URL: {result.url}")
                else:
                    print("❌ No results found")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information."""
        help_text = """
🤖 Vertex Search Agent - Help

Commands:
  help          - Show this help message
  conversation  - Start a multi-turn conversation
  search        - Enter search mode to see raw results
  config        - Show current configuration
  quit/exit/q   - Exit the application

In conversation mode:
  context <text> - Add context for future responses
  history        - Show conversation history
  back           - Return to main mode

In search mode:
  back           - Return to main mode

Examples:
  "What is artificial intelligence?"
  "Tell me about recent developments in quantum computing"
  "How does machine learning work?"
        """
        print(help_text)
    
    def show_config(self):
        """Show current configuration."""
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        config = self.agent.config
        print("\n⚙️  Current Configuration:")
        print("=" * 30)
        print(f"Project ID: {config.project_id}")
        print(f"Search Engine ID: {config.search_engine_id}")
        print(f"Location: {config.location}")
        print(f"Max Results: {config.search.max_results}")
        print(f"Grounding Threshold: {config.search.grounding_threshold}")
        print(f"Search Type: {config.search.search_type}")
        print(f"Debug Mode: {config.debug}")
        print(f"Environment: {config.environment}")
    
    def show_conversation_history(self, conversation):
        """Show conversation history."""
        history = conversation.get_history()
        
        if not history:
            print("📚 No conversation history yet")
            return
        
        print("\n📚 Conversation History:")
        print("=" * 30)
        
        for i, message in enumerate(history, 1):
            role_emoji = "👤" if message.role == "user" else "🤖"
            print(f"{i}. {role_emoji} {message.role.upper()}: {message.content[:100]}...")
            
            if message.search_results:
                print(f"   📊 Found {len(message.search_results)} search results")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Google ADK with Vertex Search Grounding - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                    # Interactive mode
  python cli.py --config config.json  # Use config file
  python cli.py --template         # Create config template
  python cli.py --question "What is AI?"  # Single question
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--template', '-t',
        action='store_true',
        help='Create a configuration template file'
    )
    
    parser.add_argument(
        '--question', '-q',
        help='Ask a single question and exit'
    )
    
    parser.add_argument(
        '--search', '-s',
        help='Perform a search and show raw results'
    )
    
    args = parser.parse_args()
    
    # Handle template creation
    if args.template:
        create_config_template()
        return
    
    # Initialize CLI
    cli = VertexSearchCLI()
    
    # Handle single question mode
    if args.question:
        await cli.initialize_agent(args.config)
        print(f"🤖 Question: {args.question}")
        response = await cli.agent.ask(args.question)
        print(f"🤖 Response: {response}")
        return
    
    # Handle search mode
    if args.search:
        await cli.initialize_agent(args.config)
        print(f"🔍 Search: {args.search}")
        results = await cli.agent.search(args.search)
        
        if results:
            print(f"\n📊 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   Score: {result.score:.3f}")
                print(f"   {result.snippet[:150]}...")
                if result.url:
                    print(f"   URL: {result.url}")
        else:
            print("❌ No results found")
        return
    
    # Interactive mode
    await cli.interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1) 