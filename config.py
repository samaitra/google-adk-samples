"""
Configuration utilities for the Google ADK with Vertex Search grounding.

This module provides utilities for loading and managing configuration
from environment variables, configuration files, and command-line arguments.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables from .env file if it exists
env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format")
    file_path: Optional[str] = Field(default=None, description="Log file path")
    
    @validator('level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()


class SearchConfig(BaseModel):
    """Configuration for search functionality."""
    max_results: int = Field(default=5, description="Maximum search results")
    grounding_threshold: float = Field(default=0.7, description="Grounding confidence threshold")
    search_type: str = Field(default="web", description="Search type")
    timeout: int = Field(default=30, description="Search timeout in seconds")
    
    @validator('grounding_threshold')
    def validate_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Grounding threshold must be between 0.0 and 1.0')
        return v
    
    @validator('max_results')
    def validate_max_results(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Max results must be between 1 and 50')
        return v


class AgentConfig(BaseModel):
    """Complete configuration for the Vertex Search Agent."""
    # Google Cloud settings
    project_id: str = Field(..., description="Google Cloud Project ID")
    search_engine_id: str = Field(..., description="Vertex Search Engine ID")
    location: str = Field(default="us-central1", description="Google Cloud region")
    
    # Search configuration
    search: SearchConfig = Field(default_factory=SearchConfig)
    
    # Logging configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Development settings
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="production", description="Environment name")
    
    class Config:
        env_prefix = "VERTEX_"
        env_nested_delimiter = "__"
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create configuration from environment variables."""
        return cls(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            search_engine_id=os.getenv("VERTEX_SEARCH_ENGINE_ID"),
            location=os.getenv("VERTEX_LOCATION", "us-central1"),
            search=SearchConfig(
                max_results=int(os.getenv("VERTEX_MAX_RESULTS", "5")),
                grounding_threshold=float(os.getenv("VERTEX_GROUNDING_THRESHOLD", "0.7")),
                search_type=os.getenv("VERTEX_SEARCH_TYPE", "web"),
                timeout=int(os.getenv("VERTEX_TIMEOUT", "30"))
            ),
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                format=os.getenv("LOG_FORMAT", "json"),
                file_path=os.getenv("LOG_FILE_PATH")
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "production")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    def validate_credentials(self) -> bool:
        """Validate that required credentials are available."""
        required_vars = [
            "GOOGLE_CLOUD_PROJECT",
            "VERTEX_SEARCH_ENGINE_ID"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return True


def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """
    Load configuration from file or environment.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        AgentConfig instance
    """
    if config_path and Path(config_path).exists():
        # Load from file (JSON/YAML support could be added here)
        pass
    
    # Load from environment variables
    config = AgentConfig.from_env()
    config.validate_credentials()
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        "project_id": "your-project-id",
        "search_engine_id": "your-search-engine-id",
        "location": "us-central1",
        "search": {
            "max_results": 5,
            "grounding_threshold": 0.7,
            "search_type": "web",
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file_path": None
        },
        "debug": False,
        "environment": "production"
    }


def create_config_template(output_path: str = "config_template.json"):
    """Create a configuration template file."""
    import json
    
    template = get_default_config()
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Configuration template created: {output_path}")


if __name__ == "__main__":
    # Create configuration template when run directly
    create_config_template() 