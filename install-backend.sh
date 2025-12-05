#!/bin/bash
# Simple installation script for Insightor

set -e

echo "🚀 Installing Insightor Backend Dependencies"
echo "=============================================="

cd "$(dirname "$0")/backend"

# Create/use virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --quiet --upgrade pip setuptools wheel

# Install packages one by one (more reliable)
echo "📦 Installing packages..."
packages=(
    "fastapi"
    "uvicorn"
    "pydantic-settings"
    "python-dotenv"
    "httpx"
    "google-generativeai"
    "tavily-python"
    "beautifulsoup4"
    "requests"
    "html2text"
)

for package in "${packages[@]}"; do
    echo "  Installing $package..."
    pip install --quiet "$package" || echo "  ⚠️  Failed to install $package, continuing..."
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate the environment, run:"
echo "  source backend/venv/bin/activate"
echo ""
echo "To run the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python run.py"
