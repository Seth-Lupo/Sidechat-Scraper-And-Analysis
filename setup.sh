#!/bin/bash

# Setup script for Sidechat scraper

echo "Setting up Sidechat scraper environment..."

# Activate virtual environment
source sidechat_scraper/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your values:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env with your Sidechat credentials"
echo ""
echo "3. Activate the virtual environment:"
echo "   source sidechat_scraper/bin/activate"
echo ""
echo "4. Run the scraper:"
echo "   python sidechat_scraper.py"