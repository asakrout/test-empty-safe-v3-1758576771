#!/usr/bin/env python3
"""Example usage of GitHub Repository Creator."""
import os
import tempfile
from repo_creator import RepositoryCreator

def example_create_python_project():
    """Example: Create a Python project repository."""
    print("🐍 Creating a Python project repository...")
    
    # Create temporary directory for the project
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define project files
        project_files = {
            "README.md": """# My Python Project

A simple Python project created with GitHub Repository Creator.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Features

- Clean project structure
- Proper dependency management
- Git integration
""",
            "main.py": """#!/usr/bin/env python3
\"\"\"Main application entry point.\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello, World!")
    print("Welcome to your new Python project!")

if __name__ == "__main__":
    main()
""",
            "requirements.txt": """requests>=2.31.0
click>=8.1.0
python-dotenv>=1.0.0
""",
            "setup.py": """from setuptools import setup, find_packages

setup(
    name="my-python-project",
    version="0.1.0",
    description="A simple Python project",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "click>=8.1.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.7",
)
""",
            ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        }
        
        try:
            creator = RepositoryCreator()
            
            result = creator.create_repository_with_files(
                repo_name="my-python-project",
                local_path=temp_dir,
                description="A simple Python project with proper structure",
                private=False,  # Public repository
                files=project_files
            )
            
            if result["success"]:
                print("✅ Python project created successfully!")
                print(f"Repository URL: {result['html_url']}")
                print(f"Clone URL: {result['clone_url']}")
            else:
                print(f"❌ Failed to create repository: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def example_create_from_existing_directory():
    """Example: Create repository from existing directory."""
    print("\n📁 Creating repository from existing directory...")
    
    # This would be used with an actual existing directory
    # For this example, we'll show the command structure
    print("To create a repository from an existing directory:")
    print("python main.py from-template my-existing-project /path/to/existing/project")
    print("  --description 'Migrating existing project to GitHub'")

def main():
    """Run examples."""
    print("🚀 GitHub Repository Creator - Examples")
    print("=" * 50)
    
    # Check if configuration is set up
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration is valid")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please run 'python main.py setup' first")
        return
    
    # Run examples
    example_create_python_project()
    example_create_from_existing_directory()
    
    print("\n📚 More examples:")
    print("1. Create a private repository:")
    print("   python main.py create my-private-repo --private")
    print()
    print("2. Create with custom description:")
    print("   python main.py create my-repo --description 'My awesome project'")
    print()
    print("3. Create from current directory:")
    print("   python main.py create my-current-project")

if __name__ == "__main__":
    main()
