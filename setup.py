#!/usr/bin/env python3
"""
Setup script for Google ADK with Vertex Search grounding.

This script helps users set up the environment and dependencies
for the Vertex Search Agent.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Check if pip is available
    if not run_command("pip --version", "Checking pip"):
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True


def setup_environment():
    """Set up environment configuration."""
    print("\n⚙️  Setting up environment...")
    
    env_file = Path("env.example")
    if not env_file.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy env.example to .env if .env doesn't exist
    if not Path(".env").exists():
        run_command("cp env.example .env", "Creating .env file from template")
        print("📝 Please edit .env file with your configuration")
    else:
        print("✅ .env file already exists")
    
    return True


def check_google_cloud():
    """Check Google Cloud setup."""
    print("\n☁️  Checking Google Cloud setup...")
    
    # Check if gcloud is installed
    if not run_command("gcloud --version", "Checking gcloud CLI"):
        print("⚠️  gcloud CLI not found. Please install it from:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    # Check if user is authenticated
    if not run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'", "Checking authentication"):
        print("⚠️  Not authenticated with Google Cloud. Please run:")
        print("   gcloud auth login")
        return False
    
    # Check if project is set
    try:
        result = subprocess.run("gcloud config get-value project", shell=True, capture_output=True, text=True)
        project = result.stdout.strip()
        if project:
            print(f"✅ Google Cloud project: {project}")
        else:
            print("⚠️  No Google Cloud project set. Please run:")
            print("   gcloud config set project YOUR_PROJECT_ID")
            return False
    except:
        print("⚠️  Could not determine Google Cloud project")
        return False
    
    return True


def enable_apis():
    """Enable required Google Cloud APIs."""
    print("\n🔌 Enabling required APIs...")
    
    apis = [
        "aiplatform.googleapis.com"
    ]
    
    for api in apis:
        if not run_command(f"gcloud services enable {api}", f"Enabling {api}"):
            print(f"⚠️  Failed to enable {api}. You may need to enable it manually in the Google Cloud Console")
    
    return True


def create_search_engine():
    """Guide user through creating a search engine."""
    print("\n🔍 Search Engine Setup")
    print("=" * 30)
    print("You need to create a Vertex Search Engine:")
    print("1. Go to Google Cloud Console")
    print("2. Navigate to Vertex AI > Search")
    print("3. Click 'Create Search Engine'")
    print("4. Choose 'Web Search' or 'Custom Search'")
    print("5. Configure your search engine")
    print("6. Copy the Search Engine ID")
    print("7. Add it to your .env file as VERTEX_SEARCH_ENGINE_ID")
    print("\nFor more details, see:")
    print("https://cloud.google.com/vertex-ai/docs/general/search")


def validate_setup():
    """Validate the setup by testing the agent."""
    print("\n🧪 Validating setup...")
    
    # Check if .env file has required variables
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_file) as f:
        env_content = f.read()
    
    required_vars = ["GOOGLE_CLOUD_PROJECT", "VERTEX_SEARCH_ENGINE_ID"]
    missing_vars = []
    
    for var in required_vars:
        if var not in env_content or f"{var}=" in env_content and "your-" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or not configured: {missing_vars}")
        print("Please edit .env file with your actual values")
        return False
    
    print("✅ Environment variables configured")
    
    # Try to import the agent
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from agent import VertexSearchAgent
        print("✅ Agent module imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import agent: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Google ADK with Vertex Search Grounding - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Check Google Cloud setup
    if not check_google_cloud():
        print("⚠️  Google Cloud setup incomplete")
        print("Please complete Google Cloud setup before continuing")
    
    # Enable APIs
    enable_apis()
    
    # Guide through search engine creation
    create_search_engine()
    
    # Validate setup
    if validate_setup():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your configuration")
        print("2. Create a Vertex Search Engine")
        print("3. Run: python cli.py")
        print("4. Or run examples: python examples/basic_usage.py")
    else:
        print("\n❌ Setup validation failed")
        print("Please complete the missing steps above")
        sys.exit(1)


if __name__ == "__main__":
    main() 