#!/bin/bash

# Alumni ML Frontend Setup Script
# This script sets up the React frontend with all dependencies

set -e

echo "========================================"
echo "Alumni ML Pipeline - Frontend Setup"
echo "========================================"
echo ""

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✓ Node.js detected: $(node --version)"
echo ""

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✓ npm detected: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created. Please update with your API URL."
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your backend API URL"
echo "2. Run: npm start"
echo ""
echo "The application will open at http://localhost:3000"
echo ""
