#!/bin/bash
# Setup script for Insightor Project
# Run this script to set up the entire project

set -e

echo "🚀 Insightor Setup Script"
echo "=========================="
echo ""

# Backend Setup
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys:"
    echo "   GOOGLE_API_KEY=your_key_here"
    echo "   TAVILY_API_KEY=your_key_here"
fi

echo "✅ Backend setup complete!"
echo ""

# Frontend Setup
echo "📦 Setting up Frontend..."
cd ../frontend

# Install dependencies
echo "Installing frontend dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo ""

# Final instructions
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "To run the application:"
echo ""
echo "1. In a terminal, start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or . venv/Scripts/activate on Windows"
echo "   python run.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
