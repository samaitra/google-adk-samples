# Quick Start Guide - Google ADK with Vertex Search Grounding

This guide will help you get up and running with the Google ADK with Vertex Search grounding in under 10 minutes.

## Prerequisites

- Python 3.8 or higher
- Google Cloud account with billing enabled
- Google Cloud CLI (gcloud) installed

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/google-adk-samples.git
cd google-adk-samples

# Run the setup script
python setup.py
```

The setup script will:
- Check your Python version
- Install dependencies
- Create environment configuration
- Check Google Cloud setup
- Enable required APIs

## Step 2: Configure Google Cloud

### 2.1 Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2.2 Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
```

### 2.3 Create a Vertex Search Engine

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Vertex AI** > **Search**
3. Click **Create Search Engine**
4. Choose **Web Search** (recommended for beginners)
5. Configure your search engine:
   - Name: `my-search-engine`
   - Description: `Search engine for grounding agent responses`
   - Search type: `Web Search`
6. Click **Create**
7. Copy the **Search Engine ID** (you'll need this for the next step)

## Step 3: Configure Environment

Edit the `.env` file with your configuration:

```bash
# Copy the example file
cp env.example .env

# Edit the file with your values
nano .env
```

Update these values in `.env`:

```env
GOOGLE_CLOUD_PROJECT=your-actual-project-id
VERTEX_SEARCH_ENGINE_ID=your-actual-search-engine-id
VERTEX_LOCATION=us-central1
```

## Step 4: Test the Setup

> **Note:** This agent uses the Vertex AI Search REST API directly (not a Python client). Authentication is handled using Google Application Default Credentials (ADC). Make sure you are authenticated with Google Cloud (e.g., `gcloud auth application-default login`).

### Option A: Interactive CLI

```bash
python cli.py
```

This will start an interactive session where you can:
- Ask questions directly
- Start conversations
- View search results
- Check configuration

### Option B: Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Conversation example
python examples/conversation_example.py

# Custom search example
python examples/custom_search.py
```

### Option C: Single Question

```bash
python cli.py --question "What are the latest developments in AI?"
```

## Step 5: Use in Your Code

```python
import asyncio
from agent import VertexSearchAgent

async def main():
    # Initialize the agent
    agent = VertexSearchAgent()
    
    # Ask a question
    response = await agent.ask("What is machine learning?")
    print(response)
    
    # Start a conversation
    conversation = agent.start_conversation()
    conversation.add_context("Focus on recent developments")
    
    response1 = await conversation.ask("What are the latest AI breakthroughs?")
    response2 = await conversation.ask("How do these compare to previous years?")
    
    print(response1)
    print(response2)

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Re-authenticate with Google Cloud
   gcloud auth application-default login
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **API Not Enabled**
   ```bash
   # Enable required APIs
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable search.googleapis.com
   ```

4. **Search Engine Not Found**
   - Verify your Search Engine ID in the `.env` file
   - Check that the search engine exists in your project
   - Ensure you have the correct permissions

### Getting Help

- Check the [full documentation](README.md)
- Run tests: `python -m pytest tests/`
- Check logs for detailed error messages
- Verify your Google Cloud setup in the console

## Next Steps

- Explore the [examples](examples/) directory
- Read the [API documentation](README.md#api-reference)
- Customize the agent configuration
- Integrate with your own applications
- Contribute to the project

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the [full documentation](README.md)
3. Check the [Google Cloud documentation](https://cloud.google.com/vertex-ai/docs/general/search)
4. Open an issue on GitHub

---

🎉 **Congratulations!** You're now ready to use the Google ADK with Vertex Search grounding! 