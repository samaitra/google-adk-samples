#!/usr/bin/env python3
"""
Simple import test for Google ADK with Vertex Search grounding.

This script tests that all required packages can be imported correctly.
"""

def test_imports():
    """Test importing all required packages."""
    print("🧪 Testing imports...")
    
    try:
        # Test Google Cloud imports
        print("📦 Testing Google Cloud imports...")
        from google.cloud import aiplatform
        print("✅ google.cloud.aiplatform imported successfully")
        
        # Test other dependencies
        print("📦 Testing other dependencies...")
        import structlog
        print("✅ structlog imported successfully")
        
        from pydantic import BaseModel, Field
        print("✅ pydantic imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        # Test our modules
        print("📦 Testing our modules...")
        from agent import VertexSearchAgent, SearchResult, Message
        print("✅ agent module imported successfully")
        
        from config import AgentConfig
        print("✅ config module imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    if not success:
        print("\n💡 Try running: pip install -r requirements.txt")
        exit(1) 