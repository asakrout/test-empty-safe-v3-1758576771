"""Configuration management for GitHub repository creator."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for GitHub repository creator."""
    
    # GitHub credentials
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    
    # Default repository settings
    DEFAULT_PRIVATE = os.getenv('DEFAULT_PRIVATE', 'false').lower() == 'true'
    DEFAULT_DESCRIPTION = os.getenv('DEFAULT_DESCRIPTION', 'Created with GitHub Repo Creator')
    
    # Branch protection settings
    SAFE_BRANCH_PATTERN = os.getenv('SAFE_BRANCH_PATTERN', '*safe*').lower()
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN is required. Please set it in your .env file or environment variables.")
        return True