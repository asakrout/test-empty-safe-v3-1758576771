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
        """Create or update branch protection rules."""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {
                    "success": False,
                    "error": f"Repository {repo_name} not found"
                }
            
            # Get the branch
            branch_ref = repo.get_branch(branch)
            
            # Apply branch protection rules
            branch_ref.edit_protection(
                required_status_checks=protection_rules.get('required_status_checks'),
                enforce_admins=protection_rules.get('enforce_admins', False),
                required_pull_request_reviews=protection_rules.get('required_pull_request_reviews'),
                restrictions=protection_rules.get('restrictions'),
                allow_force_pushes=protection_rules.get('allow_force_pushes', False),
                allow_deletions=protection_rules.get('allow_deletions', False),
                required_conversation_resolution=protection_rules.get('required_conversation_resolution', False),
                require_linear_history=protection_rules.get('require_linear_history', False)
            )
            
            logger.info(f"Successfully applied branch protection to {repo_name}:{branch}")
            return {
                "success": True,
                "message": f"Branch protection applied to {branch}"
            }
            
        except GithubException as e:
            logger.error(f"Failed to create branch protection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_branch_protection_rules(self, branch_type: str = "main") -> Dict[str, Any]:
        """Get branch protection rules based on branch type."""
        
        if branch_type == "main":
            return {
                "required_status_checks": None,  # No status checks required by default
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                    "require_last_push_approval": True
                },
                "restrictions": None,  # No user/team restrictions by default
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
                "require_linear_history": True
            }
        elif branch_type == "safe":
            # Same rules as main for *safe* branches
            return {
                "required_status_checks": None,
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                    "require_last_push_approval": True
                },
                "restrictions": None,
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
                "require_linear_history": True
            }
        else:
            return {}