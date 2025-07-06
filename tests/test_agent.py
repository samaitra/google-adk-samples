"""
Tests for the Vertex Search Agent.

This module contains unit tests and integration tests for the
Google ADK with Vertex Search grounding functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add the parent directory to the path so we can import the agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (
    VertexSearchAgent, 
    Conversation, 
    SearchResult, 
    Message, 
    AgentConfig
)
from config import load_config


class TestSearchResult:
    """Test cases for SearchResult class."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        result = SearchResult(
            title="Test Title",
            snippet="Test snippet content",
            url="https://example.com",
            score=0.85
        )
        
        assert result.title == "Test Title"
        assert result.snippet == "Test snippet content"
        assert result.url == "https://example.com"
        assert result.score == 0.85
        assert result.metadata == {}
    
    def test_search_result_defaults(self):
        """Test SearchResult with default values."""
        result = SearchResult(
            title="Test Title",
            snippet="Test snippet"
        )
        
        assert result.url is None
        assert result.score == 0.0
        assert result.metadata == {}


class TestMessage:
    """Test cases for Message class."""
    
    def test_message_creation(self):
        """Test creating a Message instance."""
        message = Message(
            role="user",
            content="Hello, world!",
            timestamp=datetime.now()
        )
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.search_results is None
        assert message.metadata == {}
    
    def test_message_with_search_results(self):
        """Test Message with search results."""
        search_results = [
            SearchResult(title="Result 1", snippet="Snippet 1"),
            SearchResult(title="Result 2", snippet="Snippet 2")
        ]
        
        message = Message(
            role="assistant",
            content="Here are the results",
            timestamp=datetime.now(),
            search_results=search_results
        )
        
        assert len(message.search_results) == 2
        assert message.search_results[0].title == "Result 1"


class TestAgentConfig:
    """Test cases for AgentConfig class."""
    
    def test_agent_config_creation(self):
        """Test creating an AgentConfig instance."""
        config = AgentConfig(
            project_id="test-project",
            search_engine_id="test-engine"
        )
        
        assert config.project_id == "test-project"
        assert config.search_engine_id == "test-engine"
        assert config.location == "us-central1"
        assert config.search.max_results == 5
    
    def test_agent_config_validation(self):
        """Test AgentConfig validation."""
        # Test invalid grounding threshold
        with pytest.raises(ValueError):
            AgentConfig(
                project_id="test-project",
                search_engine_id="test-engine",
                search=AgentConfig.__fields__['search'].type_(
                    grounding_threshold=1.5
                )
            )
        
        # Test invalid max results
        with pytest.raises(ValueError):
            AgentConfig(
                project_id="test-project",
                search_engine_id="test-engine",
                search=AgentConfig.__fields__['search'].type_(
                    max_results=100
                )
            )


class TestConversation:
    """Test cases for Conversation class."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock()
        agent._generate_response = AsyncMock(return_value=("Test response", []))
        return agent
    
    @pytest.fixture
    def conversation(self, mock_agent):
        """Create a conversation instance for testing."""
        return Conversation(mock_agent)
    
    def test_conversation_creation(self, conversation):
        """Test creating a Conversation instance."""
        assert len(conversation.messages) == 0
        assert conversation.context == ""
    
    def test_add_context(self, conversation):
        """Test adding context to conversation."""
        conversation.add_context("Focus on recent developments")
        assert conversation.context == "Focus on recent developments"
    
    def test_add_message(self, conversation):
        """Test adding messages to conversation."""
        conversation.add_message("user", "Hello")
        assert len(conversation.messages) == 1
        assert conversation.messages[0].role == "user"
        assert conversation.messages[0].content == "Hello"
    
    def test_get_history(self, conversation):
        """Test getting conversation history."""
        conversation.add_message("user", "Hello")
        conversation.add_message("assistant", "Hi there")
        
        history = conversation.get_history()
        assert len(history) == 2
        assert history[0].content == "Hello"
        assert history[1].content == "Hi there"
    
    @pytest.mark.asyncio
    async def test_ask(self, conversation):
        """Test asking a question in conversation."""
        response = await conversation.ask("What is AI?")
        
        assert response == "Test response"
        assert len(conversation.messages) == 2  # user + assistant
        assert conversation.messages[0].role == "user"
        assert conversation.messages[1].role == "assistant"


class TestVertexSearchAgent:
    """Test cases for VertexSearchAgent class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        return AgentConfig(
            project_id="test-project",
            search_engine_id="test-engine"
        )
    
    @pytest.fixture
    def agent(self, mock_config):
        """Create an agent instance for testing."""
        with patch('agent.VertexSearchService'):
            return VertexSearchAgent(config=mock_config)
    
    def test_agent_creation(self, agent):
        """Test creating a VertexSearchAgent instance."""
        assert agent.config.project_id == "test-project"
        assert agent.config.search_engine_id == "test-engine"
    
    def test_start_conversation(self, agent):
        """Test starting a conversation."""
        conversation = agent.start_conversation("test-conv")
        
        assert isinstance(conversation, Conversation)
        assert "test-conv" in agent.conversations
    
    def test_start_conversation_auto_id(self, agent):
        """Test starting a conversation with auto-generated ID."""
        conversation = agent.start_conversation()
        
        assert isinstance(conversation, Conversation)
        assert len(agent.conversations) == 1
    
    def test_get_conversation(self, agent):
        """Test getting a conversation by ID."""
        conversation = agent.start_conversation("test-conv")
        retrieved = agent.get_conversation("test-conv")
        
        assert retrieved is conversation
    
    def test_list_conversations(self, agent):
        """Test listing all conversations."""
        agent.start_conversation("conv1")
        agent.start_conversation("conv2")
        
        conversations = agent.list_conversations()
        assert "conv1" in conversations
        assert "conv2" in conversations
    
    def test_end_conversation(self, agent):
        """Test ending a conversation."""
        agent.start_conversation("test-conv")
        assert "test-conv" in agent.conversations
        
        agent.end_conversation("test-conv")
        assert "test-conv" not in agent.conversations
    
    @pytest.mark.asyncio
    async def test_search(self, agent):
        """Test performing a search."""
        mock_results = [
            SearchResult(title="Result 1", snippet="Snippet 1"),
            SearchResult(title="Result 2", snippet="Snippet 2")
        ]
        
        agent.search_service.search = AsyncMock(return_value=mock_results)
        
        results = await agent.search("test query")
        
        assert len(results) == 2
        assert results[0].title == "Result 1"
        agent.search_service.search.assert_called_once_with("test query")
    
    @pytest.mark.asyncio
    async def test_ask(self, agent):
        """Test asking a question."""
        mock_results = [
            SearchResult(title="Result 1", snippet="Snippet 1")
        ]
        
        agent.search_service.search = AsyncMock(return_value=mock_results)
        
        response = await agent.ask("What is AI?")
        
        assert "What is AI?" in response
        assert "Result 1" in response
        agent.search_service.search.assert_called_once_with("What is AI?")
    
    @pytest.mark.asyncio
    async def test_ask_no_results(self, agent):
        """Test asking a question when no results are found."""
        agent.search_service.search = AsyncMock(return_value=[])
        
        response = await agent.ask("What is AI?")
        
        assert "couldn't find any relevant information" in response.lower()
    
    @pytest.mark.asyncio
    async def test_ask_with_error(self, agent):
        """Test asking a question when search fails."""
        agent.search_service.search = AsyncMock(side_effect=Exception("Search failed"))
        
        response = await agent.ask("What is AI?")
        
        assert "encountered an error" in response.lower()


class TestIntegration:
    """Integration tests for the complete agent system."""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test a complete conversation flow."""
        with patch('agent.VertexSearchService'):
            agent = VertexSearchAgent(
                project_id="test-project",
                search_engine_id="test-engine"
            )
            
            # Mock search results
            mock_results = [
                SearchResult(title="AI Overview", snippet="Artificial Intelligence is..."),
                SearchResult(title="ML Basics", snippet="Machine Learning is a subset...")
            ]
            agent.search_service.search = AsyncMock(return_value=mock_results)
            
            # Start conversation
            conversation = agent.start_conversation("test-flow")
            conversation.add_context("Focus on technical details")
            
            # Ask questions
            response1 = await conversation.ask("What is AI?")
            response2 = await conversation.ask("How does it relate to ML?")
            
            # Verify responses
            assert "AI Overview" in response1
            assert "ML Basics" in response2
            
            # Verify conversation history
            history = conversation.get_history()
            assert len(history) == 4  # 2 user + 2 assistant messages
            
            # Verify search was called with context
            assert agent.search_service.search.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__]) 