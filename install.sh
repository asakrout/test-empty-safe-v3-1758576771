#!/bin/bash
# Installation script for GitHub Repository Creator

echo "🚀 Installing GitHub Repository Creator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make main.py executable
chmod +x main.py

# Run setup
echo "🔧 Running initial setup..."
python3 main.py setup

echo "✅ Installation complete!"
echo ""
echo "📚 Next steps:"
echo "1. Edit the .env file with your GitHub Personal Access Token"
echo "2. Get a token from: https://github.com/settings/tokens"
echo "3. Required scopes: repo, user"
echo "4. Test the installation: python3 main.py create test-repo"
echo ""
echo "🎉 Happy coding!"
