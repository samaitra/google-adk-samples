"""
Google ADK Agent with Vertex Search Grounding

This module provides a comprehensive agent implementation that uses Google's
Vertex Search API to ground responses with real-time, authoritative information.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

import structlog
from google.cloud import aiplatform
from pydantic import BaseModel, Field
import requests
from google.auth import default as google_auth_default
from google.auth.transport.requests import Request as GoogleAuthRequest

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@dataclass
class SearchResult:
    """Represents a single search result from Vertex Search."""
    title: str
    snippet: str
    url: Optional[str] = None
    score: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    search_results: Optional[List[SearchResult]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentConfig(BaseModel):
    """Configuration for the Vertex Search Agent."""
    project_id: str = Field(..., description="Google Cloud Project ID")
    search_engine_id: str = Field(..., description="Vertex Search Engine ID")
    location: str = Field(default="us-central1", description="Google Cloud region")
    max_results: int = Field(default=5, description="Maximum search results to retrieve")
    grounding_threshold: float = Field(default=0.7, description="Minimum confidence for grounding")
    search_type: str = Field(default="web", description="Type of search (web, news, etc.)")
    
    class Config:
        env_prefix = "VERTEX_"


class VertexSearchService:
    """Service for interacting with Vertex Search API via REST."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.credentials, self.project = google_auth_default()
        self._refresh_token()
    
    def _refresh_token(self):
        if not self.credentials.valid or self.credentials.expired:
            self.credentials.refresh(GoogleAuthRequest())
        self.token = self.credentials.token
    
    def _get_headers(self):
        self._refresh_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def search(self, query: str) -> List[SearchResult]:
        """Perform a search query using Vertex Search REST API."""
        url = (
            f"https://{self.config.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.config.project_id}/locations/{self.config.location}/"
            f"dataStores/{self.config.search_engine_id}/servingConfigs/default_search:search"
        )
        payload = {
            "query": query,
            "pageSize": self.config.max_results
        }
        headers = self._get_headers()
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            results = []
            for doc in data.get("results", []):
                doc_data = doc.get("document", {})
                search_result = SearchResult(
                    title=doc_data.get("title", ""),
                    snippet=doc_data.get("snippet", ""),
                    url=doc_data.get("uri", None),
                    score=doc.get("score", 0.0),
                    metadata=doc_data.get("derivedStructData", {})
                )
                results.append(search_result)
            logger.info("Search completed", query=query, result_count=len(results))
            return results
        except Exception as e:
            logger.error("Search failed", query=query, error=str(e))
            raise


class Conversation:
    """Manages a multi-turn conversation with context."""
    
    def __init__(self, agent: 'VertexSearchAgent'):
        self.agent = agent
        self.messages: List[Message] = []
        self.context: str = ""
    
    def add_context(self, context: str):
        """Add context for future responses."""
        self.context = context
        logger.info("Context added to conversation", context=context)
    
    def add_message(self, role: str, content: str, search_results: Optional[List[SearchResult]] = None):
        """Add a message to the conversation history."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            search_results=search_results
        )
        self.messages.append(message)
    
    def get_history(self) -> List[Message]:
        """Get the conversation history."""
        return self.messages.copy()
    
    async def ask(self, query: str) -> str:
        """Ask a question in the conversation context."""
        # Combine context with query
        full_query = f"{self.context} {query}".strip() if self.context else query
        
        # Add user message
        self.add_message("user", query)
        
        # Get response from agent
        response, search_results = await self.agent._generate_response(full_query, self.messages)
        
        # Add assistant message
        self.add_message("assistant", response, search_results)
        
        return response


class VertexSearchAgent:
    """
    Main agent class that uses Vertex Search for grounding responses.
    
    This agent integrates with Google's Vertex Search API to provide
    real-time, authoritative information in responses.
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        search_engine_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        **kwargs
    ):
        """
        Initialize the Vertex Search Agent.
        
        Args:
            project_id: Google Cloud Project ID
            search_engine_id: Vertex Search Engine ID
            config: Agent configuration object
            **kwargs: Additional configuration parameters
        """
        # Load configuration
        if config:
            self.config = config
        else:
            self.config = AgentConfig(
                project_id=project_id or os.getenv("GOOGLE_CLOUD_PROJECT"),
                search_engine_id=search_engine_id or os.getenv("VERTEX_SEARCH_ENGINE_ID"),
                **kwargs
            )
        
        # Initialize search service
        self.search_service = VertexSearchService(self.config)
        
        # Initialize conversation management
        self.conversations: Dict[str, Conversation] = {}
        
        logger.info("Vertex Search Agent initialized", 
                   project_id=self.config.project_id,
                   search_engine_id=self.config.search_engine_id)
    
    async def ask(self, query: str) -> str:
        """
        Ask a single question and get a grounded response.
        
        Args:
            query: The question to ask
            
        Returns:
            Grounded response based on search results
        """
        response, _ = await self._generate_response(query, [])
        return response
    
    async def search(self, query: str) -> List[SearchResult]:
        """
        Perform a search query and return raw results.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        return await self.search_service.search(query)
    
    def start_conversation(self, conversation_id: Optional[str] = None) -> Conversation:
        """
        Start a new conversation.
        
        Args:
            conversation_id: Optional conversation ID
            
        Returns:
            Conversation object for managing multi-turn interactions
        """
        if conversation_id is None:
            conversation_id = f"conv_{len(self.conversations) + 1}"
        
        conversation = Conversation(self)
        self.conversations[conversation_id] = conversation
        
        logger.info("New conversation started", conversation_id=conversation_id)
        return conversation
    
    async def _generate_response(self, query: str, conversation_history: List[Message]) -> tuple[str, List[SearchResult]]:
        """
        Generate a grounded response based on search results.
        
        Args:
            query: The user query
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (response_text, search_results)
        """
        try:
            # Perform search
            search_results = await self.search_service.search(query)
            
            if not search_results:
                logger.warning("No search results found", query=query)
                return "I couldn't find any relevant information for your query.", []
            
            # Generate response based on search results
            response = self._synthesize_response(query, search_results, conversation_history)
            
            logger.info("Response generated", 
                       query=query, 
                       result_count=len(search_results),
                       response_length=len(response))
            
            return response, search_results
            
        except Exception as e:
            logger.error("Failed to generate response", query=query, error=str(e))
            return f"I encountered an error while searching for information: {str(e)}", []
    
    def _synthesize_response(self, query: str, search_results: List[SearchResult], conversation_history: List[Message]) -> str:
        """
        Synthesize a response based on search results and conversation history.
        
        Args:
            query: The user query
            search_results: List of search results
            conversation_history: Previous conversation messages
            
        Returns:
            Synthesized response
        """
        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"{i}. {result.title}: {result.snippet}")
        
        search_context = "\n".join(context_parts)
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 messages
            conversation_context = "\n".join([
                f"{msg.role}: {msg.content}" for msg in recent_messages
            ])
        
        # Create the response
        response = f"""Based on my search results, here's what I found regarding your query: "{query}"

{search_context}

This information is grounded in current search results from authoritative sources. If you need more specific details or have follow-up questions, please let me know!"""
        
        return response
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self) -> List[str]:
        """List all active conversation IDs."""
        return list(self.conversations.keys())
    
    def end_conversation(self, conversation_id: str):
        """End a conversation and remove it from memory."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info("Conversation ended", conversation_id=conversation_id)


# Convenience function for quick usage
async def create_agent(
    project_id: Optional[str] = None,
    search_engine_id: Optional[str] = None,
    **kwargs
) -> VertexSearchAgent:
    """
    Create a Vertex Search Agent with default configuration.
    
    Args:
        project_id: Google Cloud Project ID
        search_engine_id: Vertex Search Engine ID
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured VertexSearchAgent instance
    """
    return VertexSearchAgent(project_id=project_id, search_engine_id=search_engine_id, **kwargs) 