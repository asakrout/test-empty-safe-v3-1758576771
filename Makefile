# GitHub Repository Creator Makefile

.PHONY: install setup test clean help

# Default target
help:
	@echo "GitHub Repository Creator - Available commands:"
	@echo ""
	@echo "  install    - Install dependencies and setup"
	@echo "  setup      - Setup GitHub credentials"
	@echo "  test       - Run tests"
	@echo "  clean      - Clean up temporary files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install    # Install everything"
	@echo "  make setup      # Setup GitHub credentials"
	@echo "  make test       # Test the application"

# Install dependencies and setup
install:
	@echo "🚀 Installing GitHub Repository Creator..."
	pip3 install -r requirements.txt
	chmod +x main.py
	@echo "✅ Installation complete!"

# Setup GitHub credentials
setup:
	@echo "🔧 Setting up GitHub credentials..."
	python3 main.py setup

# Run tests
test:
	@echo "🧪 Running tests..."
	python3 test_app.py

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleanup complete!"

# Create a sample repository (requires setup)
sample:
	@echo "📁 Creating sample repository..."
	python3 main.py create sample-repo-$(shell date +%s) --description "Sample repository created with make"
