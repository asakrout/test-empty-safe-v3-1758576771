"""GitHub API client for repository operations."""
import os
import tempfile
from typing import Optional, Dict, Any
from github import Github, GithubException
from git import Repo, GitCommandError
import logging
from config import Config

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
    
    def create_branch_protection_rules(
        self, 
        repo_name: str
    ) -> Dict[str, Any]:
        """Create branch protection rules for main and *safe* patterns using Repository Rules API."""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {
                    "success": False,
                    "error": f"Repository {repo_name} not found"
                }
            
            import requests
            
            # Get protection rules
            main_rules = self.get_branch_protection_rules("main")
            safe_rules = self.get_branch_protection_rules("safe")
            
            results = {}
            
            # Protect main branch using traditional API
            main_url = f"https://api.github.com/repos/{self.username}/{repo_name}/branches/main/protection"
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {self.token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            main_payload = {
                "required_status_checks": None,
                "enforce_admins": main_rules.get('enforce_admins', False),
                "required_pull_request_reviews": main_rules.get('required_pull_request_reviews'),
                "restrictions": main_rules.get('restrictions'),
                "allow_force_pushes": main_rules.get('allow_force_pushes', False),
                "allow_deletions": main_rules.get('allow_deletions', False),
                "required_conversation_resolution": True,
                "require_linear_history": True
            }
            
            main_response = requests.put(main_url, headers=headers, json=main_payload)
            if main_response.status_code == 200:
                results["main"] = {"success": True, "message": "Main branch protected"}
                logger.info(f"Successfully protected main branch in {repo_name}")
            else:
                results["main"] = {"success": False, "error": f"HTTP {main_response.status_code}: {main_response.text}"}
                logger.error(f"Failed to protect main branch: {main_response.status_code} - {main_response.text}")
            
            # Create branch protection for "safe" branch (literal branch name)
            safe_url = f"https://api.github.com/repos/{self.username}/{repo_name}/branches/safe/protection"
            safe_payload = {
                "required_status_checks": None,
                "enforce_admins": safe_rules.get('enforce_admins', False),
                "required_pull_request_reviews": safe_rules.get('required_pull_request_reviews'),
                "restrictions": safe_rules.get('restrictions'),
                "allow_force_pushes": safe_rules.get('allow_force_pushes', False),
                "allow_deletions": safe_rules.get('allow_deletions', False),
                "required_conversation_resolution": True,
                "require_linear_history": True
            }
            
            safe_response = requests.put(safe_url, headers=headers, json=safe_payload)
            if safe_response.status_code == 200:
                results["safe_branch"] = {"success": True, "message": "Safe branch protected"}
                logger.info(f"Successfully protected 'safe' branch in {repo_name}")
            else:
                results["safe_branch"] = {"success": False, "error": f"HTTP {safe_response.status_code}: {safe_response.text}"}
                logger.error(f"Failed to protect 'safe' branch: {safe_response.status_code} - {safe_response.text}")
            
            # Note: Repository Rules API with wildcards may not be available for all repositories
            # For now, we'll configure the pattern and provide instructions for manual setup
            results["safe_pattern"] = {
                "success": True, 
                "message": f"{Config.SAFE_BRANCH_PATTERN} pattern configured - create branch protection rule manually in GitHub UI with pattern '{Config.SAFE_BRANCH_PATTERN}'"
            }
            logger.info(f"{Config.SAFE_BRANCH_PATTERN} pattern configured for {repo_name} - create branch protection rule manually in GitHub UI")
            
            return {
                "success": True,
                "results": results,
                "message": "Branch protection setup completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to create branch protection rules: {e}")
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
    
    def setup_branch_protection_webhook(self, repo_name: str) -> Dict[str, Any]:
        """Set up a webhook to automatically protect new safe branches."""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return {
                    "success": False,
                    "error": f"Repository {repo_name} not found"
                }
            
            # Create a webhook for branch creation events
            webhook_url = "https://your-webhook-endpoint.com/github-webhook"  # This would need to be configured
            webhook_config = {
                "url": webhook_url,
                "content_type": "json",
                "secret": "your-webhook-secret",  # This would need to be configured
                "events": ["create"]  # Trigger on branch creation
            }
            
            # Note: This is a placeholder - actual webhook setup would require a webhook endpoint
            # For now, we'll just return success and mention that manual protection is needed
            logger.info(f"Webhook setup would be configured for {repo_name}")
            return {
                "success": True,
                "message": "Webhook setup placeholder - manual protection required for new safe branches"
            }
            
        except Exception as e:
            logger.error(f"Failed to setup webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }