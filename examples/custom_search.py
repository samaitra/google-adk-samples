#!/usr/bin/env python3
"""
Custom search example for the Vertex Search Agent.

This example demonstrates how to:
1. Configure custom search parameters
2. Process search results
3. Filter and analyze results
4. Use different search types
"""

import asyncio
import os
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import VertexSearchAgent, AgentConfig

# Load environment variables
load_dotenv()


async def main():
    """Main function demonstrating custom search usage."""
    
    # Create custom configuration
    config = AgentConfig(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        search_engine_id=os.getenv("VERTEX_SEARCH_ENGINE_ID"),
        max_results=10,
        grounding_threshold=0.8,
        search_type="web"
    )
    
    # Initialize the agent with custom config
    agent = VertexSearchAgent(config=config)
    
    print("🤖 Vertex Search Agent - Custom Search Example")
    print("=" * 50)
    
    # Example search queries
    search_queries = [
        "quantum computing breakthroughs 2024",
        "sustainable energy solutions",
        "machine learning applications in healthcare",
        "cybersecurity threats and solutions"
    ]
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n🔍 Search Query {i}: {query}")
        print("-" * 40)
        
        try:
            # Perform search and get raw results
            search_results = await agent.search(query)
            
            print(f"📊 Found {len(search_results)} results:")
            
            # Process and display results
            for j, result in enumerate(search_results, 1):
                print(f"\n  {j}. {result.title}")
                print(f"     Score: {result.score:.3f}")
                print(f"     Snippet: {result.snippet[:150]}...")
                if result.url:
                    print(f"     URL: {result.url}")
                
                # Display metadata if available
                if result.metadata:
                    print(f"     Metadata: {len(result.metadata)} fields")
            
            # Analyze results
            if search_results:
                avg_score = sum(r.score for r in search_results) / len(search_results)
                print(f"\n📈 Analysis:")
                print(f"   Average score: {avg_score:.3f}")
                print(f"   Highest score: {max(r.score for r in search_results):.3f}")
                print(f"   Lowest score: {min(r.score for r in search_results):.3f}")
                
                # Filter high-quality results
                high_quality = [r for r in search_results if r.score > 0.8]
                print(f"   High-quality results (score > 0.8): {len(high_quality)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Add a small delay between searches
        await asyncio.sleep(1)
    
    print("\n✅ Example completed!")


async def demonstrate_search_types():
    """Demonstrate different search types."""
    
    print("\n🔄 Demonstrating Different Search Types")
    print("=" * 40)
    
    # Test different search configurations
    search_configs = [
        {"search_type": "web", "max_results": 5, "description": "Web Search"},
        {"search_type": "news", "max_results": 3, "description": "News Search"},
        {"search_type": "academic", "max_results": 4, "description": "Academic Search"}
    ]
    
    for config in search_configs:
        print(f"\n📋 {config['description']}")
        print("-" * 20)
        
        try:
            # Create agent with specific config
            agent_config = AgentConfig(
                project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
                search_engine_id=os.getenv("VERTEX_SEARCH_ENGINE_ID"),
                search_type=config["search_type"],
                max_results=config["max_results"]
            )
            
            agent = VertexSearchAgent(config=agent_config)
            
            # Perform search
            results = await agent.search("artificial intelligence")
            
            print(f"Found {len(results)} results")
            for result in results[:2]:  # Show first 2 results
                print(f"  - {result.title}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    # Uncomment to test different search types
    # asyncio.run(demonstrate_search_types()) 