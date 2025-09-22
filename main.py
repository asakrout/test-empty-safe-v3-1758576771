#!/usr/bin/env python3
"""Main CLI interface for GitHub repository creator."""
import os
import sys
import logging
from pathlib import Path
import click

from repo_creator import RepositoryCreator
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """GitHub Repository Creator - Create and push repositories to GitHub."""
    pass

@cli.command()
@click.argument('repo_name')
@click.option('--description', '-d', default='', help='Repository description')
@click.option('--private', '-p', is_flag=True, help='Make repository private')
@click.option('--local-path', '-l', default='.', help='Local directory path (default: current directory)')
@click.option('--files', '-f', help='Path to JSON file containing files to create')
def create(repo_name, description, private, local_path, files):
    """Create a new GitHub repository and push local files."""
    try:
        creator = RepositoryCreator()
        
        # Load custom files if provided
        custom_files = None
        if files and os.path.exists(files):
            import json
            with open(files, 'r') as f:
                custom_files = json.load(f)
        
        result = creator.create_repository_with_files(
            repo_name=repo_name,
            local_path=os.path.abspath(local_path),
            description=description,
            private=private,
            files=custom_files
        )
        
        if result["success"]:
            click.echo(click.style("✅ Success!", fg="green"))
            click.echo(f"Repository: {result['html_url']}")
            click.echo(f"Clone URL: {result['clone_url']}")
            click.echo(f"Local path: {result['local_path']}")
            
            # Display branch protection information
            if "branch_protection" in result:
                protection = result["branch_protection"]
                if protection["success"]:
                    click.echo(click.style("🛡️ Branch Protection Setup:", fg="blue"))
                    click.echo("  ✅ main branch: protected")
                    click.echo("  ✅ safe branch: protected")
                    click.echo(f"  ✅ {Config.SAFE_BRANCH_PATTERN} pattern: configured")
                else:
                    click.echo(click.style("⚠️ Branch protection failed:", fg="yellow"))
                    click.echo(f"  {protection['error']}")
        else:
            click.echo(click.style("❌ Error:", fg="red"))
            click.echo(result["error"])
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
@click.argument('repo_name')
@click.argument('template_path')
@click.option('--description', '-d', default='', help='Repository description')
@click.option('--private', '-p', is_flag=True, help='Make repository private')
def from_template(repo_name, template_path, description, private):
    """Create a repository from an existing local directory."""
    try:
        creator = RepositoryCreator()
        
        result = creator.create_from_template(
            repo_name=repo_name,
            template_path=os.path.abspath(template_path),
            description=description,
            private=private
        )
        
        if result["success"]:
            click.echo(click.style("✅ Success!", fg="green"))
            click.echo(f"Repository: {result['html_url']}")
            click.echo(f"Clone URL: {result['clone_url']}")
            click.echo(f"Template path: {result['template_path']}")
            
            # Display branch protection information
            if "branch_protection" in result:
                protection = result["branch_protection"]
                if protection["success"]:
                    click.echo(click.style("🛡️ Branch Protection Setup:", fg="blue"))
                    click.echo("  ✅ main branch: protected")
                    click.echo("  ✅ safe branch: protected")
                    click.echo(f"  ✅ {Config.SAFE_BRANCH_PATTERN} pattern: configured")
                else:
                    click.echo(click.style("⚠️ Branch protection failed:", fg="yellow"))
                    click.echo(f"  {protection['error']}")
        else:
            click.echo(click.style("❌ Error:", fg="red"))
            click.echo(result["error"])
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
def test():
    """Test GitHub connection and authentication."""
    try:
        click.echo("🔍 Testing GitHub connection...")
        creator = RepositoryCreator()
        
        # Test GitHub API connection
        user = creator.github_client.user
        click.echo(f"✅ Connected as: {user.login}")
        click.echo(f"📧 Email: {user.email or 'Not public'}")
        click.echo(f"🏢 Company: {user.company or 'Not specified'}")
        click.echo(f"📊 Public repos: {user.public_repos}")
        
        # Test repository listing
        repos = list(user.get_repos()[:5])  # Get first 5 repos
        click.echo(f"\n📁 Recent repositories:")
        for repo in repos:
            click.echo(f"  - {repo.name} ({'🔒' if repo.private else '🌐'})")
        
        click.echo("\n✅ GitHub connection test successful!")
        
    except Exception as e:
        click.echo(click.style(f"❌ GitHub connection failed: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
@click.argument('repo_name')
@click.option('--branch', '-b', default='main', help='Branch to protect (default: main)')
@click.option('--type', '-t', type=click.Choice(['main', 'safe']), default='main', help='Protection type (main or safe)')
def protect(repo_name, branch, type):
    """Apply branch protection rules to an existing repository."""
    try:
        creator = RepositoryCreator()
        
        # Get protection rules based on type
        rules = creator.github_client.get_branch_protection_rules(type)
        
        # Apply protection
        result = creator.github_client.create_branch_protection(
            repo_name=repo_name,
            branch=branch,
            protection_rules=rules
        )
        
        if result["success"]:
            click.echo(click.style("✅ Branch protection applied successfully!", fg="green"))
            click.echo(f"Repository: {repo_name}")
            click.echo(f"Branch: {branch}")
            click.echo(f"Type: {type}")
            click.echo(f"Message: {result['message']}")
        else:
            click.echo(click.style("❌ Failed to apply branch protection:", fg="red"))
            click.echo(result["error"])
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
@click.argument('repo_name')
@click.argument('branch_name')
def create_branch(repo_name, branch_name):
    """Create a new branch in an existing repository."""
    try:
        creator = RepositoryCreator()
        
        # Get the repository
        repo = creator.github_client.get_repository(repo_name)
        if not repo:
            click.echo(click.style(f"❌ Repository {repo_name} not found", fg="red"))
            sys.exit(1)
        
        # Create the branch from main
        try:
            main_branch = repo.get_branch("main")
            new_branch = repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=main_branch.commit.sha
            )
            
            click.echo(click.style("✅ Branch created successfully!", fg="green"))
            click.echo(f"Repository: {repo_name}")
            click.echo(f"Branch: {branch_name}")
            
            # Check if the branch matches the safe pattern
            if Config.get_safe_pattern_core() in branch_name.lower():
                click.echo(click.style(f"🛡️ Branch '{branch_name}' matches '{Config.SAFE_BRANCH_PATTERN}' pattern", fg="blue"))
            
        except Exception as e:
            click.echo(click.style(f"❌ Failed to create branch: {e}", fg="red"))
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
@click.argument('repo_name')
def protect_safe_branches(repo_name):
    """Apply safe branch protection to all existing branches matching the configured pattern."""
    try:
        creator = RepositoryCreator()
        
        # Get the repository
        repo = creator.github_client.get_repository(repo_name)
        if not repo:
            click.echo(click.style(f"❌ Repository {repo_name} not found", fg="red"))
            sys.exit(1)
        
        # Get all branches matching the safe pattern
        branches = repo.get_branches()
        safe_branches = [branch for branch in branches if Config.get_safe_pattern_core() in branch.name.lower()]
        
        if not safe_branches:
            click.echo(click.style(f"ℹ️ No branches matching '{Config.SAFE_BRANCH_PATTERN}' pattern found", fg="blue"))
            return
        
        click.echo(click.style(f"🛡️ Found {len(safe_branches)} branches matching '{Config.SAFE_BRANCH_PATTERN}' pattern:", fg="blue"))
        
        safe_rules = creator.github_client.get_branch_protection_rules("safe")
        protected_count = 0
        
        for branch in safe_branches:
            click.echo(f"  - {branch.name}")
            protection_result = creator.github_client.create_branch_protection(
                repo_name=repo_name,
                branch=branch.name,
                protection_rules=safe_rules
            )
            
            if protection_result["success"]:
                click.echo(click.style(f"    ✅ Protected {branch.name}", fg="green"))
                protected_count += 1
            else:
                click.echo(click.style(f"    ❌ Failed to protect {branch.name}: {protection_result['error']}", fg="red"))
        
        click.echo(click.style(f"\n✅ Successfully protected {protected_count}/{len(safe_branches)} branches matching '{Config.SAFE_BRANCH_PATTERN}' pattern", fg="green"))
            
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))
        import traceback
        click.echo(f"Full error details: {traceback.format_exc()}")
        sys.exit(1)

@cli.command()
def setup():
    """Setup GitHub credentials and configuration."""
    click.echo("🔧 Setting up GitHub Repository Creator...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        click.echo("📄 .env file already exists")
    else:
        # Copy from example
        example_file = Path('env.example')
        if example_file.exists():
            import shutil
            shutil.copy('env.example', '.env')
            click.echo("📄 Created .env file from template")
        else:
            click.echo("❌ env.example file not found")
            return
    
    click.echo("\n📝 Please edit the .env file with your GitHub credentials:")
    click.echo("   1. Get a Personal Access Token from: https://github.com/settings/tokens")
    click.echo("   2. Required scopes: repo, user")
    click.echo("   3. Set GITHUB_TOKEN in your .env file")
    click.echo("   4. Optionally set GITHUB_USERNAME")
    
    # Test configuration
    try:
        Config.validate()
        click.echo("\n✅ Configuration is valid!")
    except ValueError as e:
        click.echo(f"\n❌ Configuration error: {e}")

if __name__ == '__main__':
    cli()