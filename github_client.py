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
        self.token = token  # Store token for direct API calls
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
            # Prepare parameters, only include non-None values
            repo_params = {
                'name': name,
                'description': description,
                'private': private,
                'auto_init': auto_init
            }
            
            if gitignore_template is not None:
                repo_params['gitignore_template'] = gitignore_template
            if license_template is not None:
                repo_params['license_template'] = license_template
                
            repo = self.user.create_repo(**repo_params)
            
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
    
    def create_branch_protection(
        self, 
        repo_name: str, 
        branch: str, 
        protection_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create or update branch protection rules using REST API."""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {
                    "success": False,
                    "error": f"Repository {repo_name} not found"
                }
            
            # Use the REST API directly for branch protection
            import requests
            
            url = f"https://api.github.com/repos/{self.username}/{repo_name}/branches/{branch}/protection"
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {self.token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            # Prepare the protection rules payload
            payload = {
                "required_status_checks": None,
                "enforce_admins": protection_rules.get('enforce_admins', False),
                "required_pull_request_reviews": protection_rules.get('required_pull_request_reviews'),
                "restrictions": protection_rules.get('restrictions'),
                "allow_force_pushes": protection_rules.get('allow_force_pushes', False),
                "allow_deletions": protection_rules.get('allow_deletions', False),
                "required_conversation_resolution": True,
                "require_linear_history": True
            }
            
            response = requests.put(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Successfully applied branch protection to {repo_name}:{branch}")
                return {
                    "success": True,
                    "message": f"Branch protection applied to {branch}"
                }
            else:
                logger.error(f"Failed to create branch protection: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
        except Exception as e:
            logger.error(f"Failed to create branch protection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_branch_protection_rules(self, branch_type: str = "main") -> Dict[str, Any]:
        """Get branch protection rules based on branch type."""
        
        if branch_type == "main":
            return {
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True
                },
                "restrictions": None,  # No user/team restrictions by default
                "allow_force_pushes": False,
                "allow_deletions": False
            }
        elif branch_type == "safe":
            # Same rules as main for *safe* branches
            return {
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True
                },
                "restrictions": None,
                "allow_force_pushes": False,
                "allow_deletions": False
            }
        else:
            return {}