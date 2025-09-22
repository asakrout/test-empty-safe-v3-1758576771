"""GitHub API client for repository operations."""
import os
import tempfile
from typing import Optional, Dict, Any
from github import Github, GithubException
from git import Repo, GitCommandError
import logging

logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for interacting with GitHub API and Git operations."""
    
    def __init__(self, token: str, username: Optional[str] = None):
        """Initialize GitHub client with authentication token."""
        self.github = Github(token)
        self.username = username or self.github.get_user().login
        self.user = self.github.get_user()
        
    def create_repository(
        self, 
        name: str, 
        description: str = "", 
        private: bool = False,
        auto_init: bool = True,
        gitignore_template: Optional[str] = None,
        license_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new GitHub repository."""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                license_template=license_template
            )
            
            logger.info(f"Successfully created repository: {repo.full_name}")
            return {
                "success": True,
                "repo": repo,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "html_url": repo.html_url
            }
        except GithubException as e:
            logger.error(f"Failed to create repository: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def push_to_repository(
        self, 
        local_path: str, 
        repo_url: str, 
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Push local repository to GitHub."""
        try:
            # Initialize git repository if not already done
            if not os.path.exists(os.path.join(local_path, '.git')):
                repo = Repo.init(local_path)
            else:
                repo = Repo(local_path)
            
            # Add remote origin
            try:
                origin = repo.remote('origin')
                origin.set_url(repo_url)
            except:
                origin = repo.create_remote('origin', repo_url)
            
            # Add all files
            repo.git.add('.')
            
            # Check if there are any changes to commit
            if repo.is_dirty() or repo.untracked_files:
                # Commit changes
                repo.index.commit('Initial commit')
                logger.info("Committed initial changes")
            
            # Push to remote
            origin.push(refspec=f'{branch}:{branch}')
            logger.info(f"Successfully pushed to {repo_url}")
            
            return {
                "success": True,
                "message": f"Successfully pushed to {repo_url}"
            }
            
        except GitCommandError as e:
            logger.error(f"Git operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error during push: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_repository(self, repo_name: str) -> Optional[Any]:
        """Get repository by name."""
        try:
            return self.user.get_repo(repo_name)
        except GithubException:
            return None