"""Main repository creation and management logic."""
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from github_client import GitHubClient
from config import Config

logger = logging.getLogger(__name__)

class RepositoryCreator:
    """Main class for creating and pushing GitHub repositories."""
    
    def __init__(self):
        """Initialize repository creator with GitHub client."""
        Config.validate()
        self.github_client = GitHubClient(Config.GITHUB_TOKEN, Config.GITHUB_USERNAME)
    
    def create_repository_with_files(
        self,
        repo_name: str,
        local_path: str,
        description: str = "",
        private: bool = False,
        files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a GitHub repository and push local files to it."""
        
        # Default files to create if none provided
        if files is None:
            files = {
                "README.md": f"# {repo_name}\n\n{description or 'A new repository'}\n",
                ".gitignore": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Virtual environments\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# OS\n.DS_Store\nThumbs.db\n"
            }
        
        # Create local files
        self._create_local_files(local_path, files)
        
        # Create GitHub repository
        repo_result = self.github_client.create_repository(
            name=repo_name,
            description=description or Config.DEFAULT_DESCRIPTION,
            private=private
        )
        
        if not repo_result["success"]:
            return repo_result
        
        # Push to GitHub
        push_result = self.github_client.push_to_repository(
            local_path=local_path,
            repo_url=repo_result["clone_url"]
        )
        
        if not push_result["success"]:
            return push_result
        
        # Apply branch protection rules
        protection_result = self._apply_branch_protections(repo_name)
        
        return {
            "success": True,
            "repository": repo_result["repo"],
            "clone_url": repo_result["clone_url"],
            "html_url": repo_result["html_url"],
            "local_path": local_path,
            "branch_protection": protection_result,
            "message": f"Repository '{repo_name}' created, pushed, and protected successfully!"
        }
    
    def _create_local_files(self, local_path: str, files: Dict[str, str]) -> None:
        """Create local files in the specified directory."""
        os.makedirs(local_path, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = os.path.join(local_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
    
    def _apply_branch_protections(self, repo_name: str) -> Dict[str, Any]:
        """Apply branch protection rules to the repository."""
        try:
            # Create branch protection rules for main and *safe* pattern
            result = self.github_client.create_branch_protection_rules(repo_name)
            
            logger.info("Branch protection setup complete:")
            logger.info("- main branch: protected")
            logger.info("- safe branch: rule configured")
            logger.info(f"- {Config.SAFE_BRANCH_PATTERN} pattern: configured")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply branch protections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_from_template(
        self,
        repo_name: str,
        template_path: str,
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """Create repository from an existing local directory."""
        
        if not os.path.exists(template_path):
            return {
                "success": False,
                "error": f"Template path does not exist: {template_path}"
            }
        
        # Create GitHub repository
        repo_result = self.github_client.create_repository(
            name=repo_name,
            description=description or Config.DEFAULT_DESCRIPTION,
            private=private
        )
        
        if not repo_result["success"]:
            return repo_result
        
        # Push existing directory to GitHub
        push_result = self.github_client.push_to_repository(
            local_path=template_path,
            repo_url=repo_result["clone_url"]
        )
        
        if not push_result["success"]:
            return push_result
        
        # Apply branch protection rules
        protection_result = self._apply_branch_protections(repo_name)
        
        return {
            "success": True,
            "repository": repo_result["repo"],
            "clone_url": repo_result["clone_url"],
            "html_url": repo_result["html_url"],
            "template_path": template_path,
            "branch_protection": protection_result,
            "message": f"Repository '{repo_name}' created from template, pushed, and protected successfully!"
        }