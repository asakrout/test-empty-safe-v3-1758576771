# GitHub Repository Creator

A Python application that creates and pushes GitHub repositories using your login credentials.

## Features

- 🔐 **Secure Authentication** - Uses GitHub Personal Access Tokens
- 📁 **Create Repositories** - Create new repositories with custom settings
- 📤 **Push Local Code** - Push existing local directories to GitHub
- 🎨 **Template Support** - Create repositories from templates
- ⚙️ **Configurable** - Customize repository settings via environment variables
- 🖥️ **CLI Interface** - Easy-to-use command-line interface

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd github-branch-protect

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup GitHub Credentials

```bash
# Run the setup command
python main.py setup
```

This will:
- Create a `.env` file from the template
- Guide you through setting up your GitHub Personal Access Token

### 3. Get GitHub Personal Access Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` and `user`
4. Copy the token and add it to your `.env` file

### 4. Create Your First Repository

```bash
# Create a repository from current directory
python main.py create my-awesome-repo --description "My awesome project"

# Create a private repository
python main.py create my-private-repo --private

# Create from a specific directory
python main.py create my-project --local-path /path/to/my/project
```

## Usage

### Create Repository from Current Directory

```bash
python main.py create <repo-name> [options]
```

**Options:**
- `--description, -d`: Repository description
- `--private, -p`: Make repository private
- `--local-path, -l`: Local directory path (default: current directory)
- `--files, -f`: Path to JSON file containing files to create

### Create Repository from Template

```bash
python main.py from-template <repo-name> <template-path> [options]
```

**Options:**
- `--description, -d`: Repository description
- `--private, -p`: Make repository private

### Setup Configuration

```bash
python main.py setup
```

## Configuration

The application uses a `.env` file for configuration:

```env
# GitHub Personal Access Token (required)
GITHUB_TOKEN=your_github_token_here

# GitHub username (optional, will be detected from token)
GITHUB_USERNAME=your_username

# Default repository settings
DEFAULT_PRIVATE=false
DEFAULT_DESCRIPTION=Created with GitHub Repo Creator
```

## Examples

### Example 1: Create a Python Project

```bash
# Create a Python project repository
python main.py create my-python-project \
  --description "A Python project with proper structure" \
  --private
```

### Example 2: Create from Existing Directory

```bash
# Create repository from existing project
python main.py from-template my-existing-project /path/to/existing/project \
  --description "Migrating existing project to GitHub"
```

### Example 3: Create with Custom Files

Create a `files.json` file:
```json
{
  "README.md": "# My Project\n\nThis is my awesome project!",
  "src/main.py": "print('Hello, World!')",
  "requirements.txt": "requests>=2.31.0",
  ".gitignore": "*.pyc\n__pycache__/\n.env"
}
```

Then run:
```bash
python main.py create my-custom-repo --files files.json
```

## Requirements

- Python 3.7+
- GitHub Personal Access Token with `repo` and `user` scopes
- Git installed and configured

## Dependencies

- `requests` - HTTP library
- `PyGithub` - GitHub API wrapper
- `python-dotenv` - Environment variable management
- `click` - CLI framework
- `gitpython` - Git operations

## Troubleshooting

### Common Issues

1. **"GITHUB_TOKEN is required"**
   - Make sure you've set up your `.env` file with a valid GitHub token
   - Run `python main.py setup` to configure

2. **"Repository already exists"**
   - Choose a different repository name
   - Or delete the existing repository on GitHub

3. **"Git operation failed"**
   - Make sure Git is installed and configured
   - Check that you have write permissions to the local directory

4. **"Authentication failed"**
   - Verify your GitHub token is valid and has the correct scopes
   - Check that the token hasn't expired

### Getting Help

- Check the logs for detailed error messages
- Verify your GitHub token has the required scopes
- Ensure Git is properly configured on your system

## License

MIT License - feel free to use and modify as needed.
