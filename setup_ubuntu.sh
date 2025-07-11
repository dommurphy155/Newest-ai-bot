#!/bin/bash
# Lightweight Trading Bot Setup for Ubuntu 20.04 Python 3.8
# Optimized installation without heavy dependencies like TA-Lib

set -e

echo "🚀 Setting up Lightweight AI Trading Bot for Ubuntu 20.04..."
echo "=================================================="

# Check Ubuntu version
if [[ $(lsb_release -rs) != "20.04" ]]; then
    echo "⚠️  Warning: This script is optimized for Ubuntu 20.04"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ ${PYTHON_VERSION:0:3} != "3.8" ]]; then
    echo "⚠️  Warning: Python 3.8 recommended, found $PYTHON_VERSION"
fi

echo "✅ Python version: $PYTHON_VERSION"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install essential system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    curl \
    git \
    sqlite3 \
    libssl-dev \
    libffi-dev \
    pkg-config

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install lightweight requirements
echo "📋 Installing lightweight Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data

# Set up environment file template
echo "🔐 Creating environment template..."
cat > .env.template << EOF
# OANDA API Configuration
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_ENVIRONMENT=practice

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Optional: HuggingFace Token for advanced features
HF_TOKEN=your_huggingface_token_here
EOF

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Please copy .env.template to .env and fill in your credentials:"
    echo "   cp .env.template .env"
    echo "   nano .env"
fi

# Set permissions
echo "🔒 Setting permissions..."
chmod +x main.py
chmod 644 .env.template
chmod -R 755 logs data

# Create systemd service file (optional)
echo "🔧 Creating systemd service template..."
cat > trading-bot.service.template << EOF
[Unit]
Description=Lightweight AI Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Run quick tests
echo "🧪 Running quick system tests..."

# Test Python imports
echo "Testing Python imports..."
python3 -c "
import sys
import asyncio
import numpy as np
import pandas as pd
import aiohttp
import oandapyV20
print('✅ All core imports successful')
"

# Test technical analysis
echo "Testing technical analysis..."
python3 -c "
from technical_analysis import TechnicalAnalyzer
analyzer = TechnicalAnalyzer()
print('✅ Technical analysis module working')
"

# Memory usage check
echo "📊 Checking memory usage..."
python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'Available memory: {mem.available / (1024**3):.1f} GB')
if mem.available < 1024**3:  # Less than 1GB
    print('⚠️  Warning: Low memory available')
else:
    print('✅ Memory check passed')
"

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================="
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.template to .env and configure your API keys:"
echo "   cp .env.template .env"
echo "   nano .env"
echo ""
echo "2. Test the bot:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "3. (Optional) Install as system service:"
echo "   sudo cp trading-bot.service.template /etc/systemd/system/trading-bot.service"
echo "   sudo systemctl enable trading-bot"
echo "   sudo systemctl start trading-bot"
echo ""
echo "📖 Features included:"
echo "   ✅ Lightweight technical analysis (no TA-Lib dependency)"
echo "   ✅ OANDA API integration"
echo "   ✅ Telegram bot interface"
echo "   ✅ SQLite database (no heavy database required)"
echo "   ✅ News sentiment analysis"
echo "   ✅ Risk management"
echo "   ✅ Real-time monitoring"
echo ""
echo "💾 Memory footprint: ~100-200MB (vs ~1GB+ with heavy libraries)"
echo "⚡ Installation size: ~50MB (vs ~500MB+ with TA-Lib/QuantLib)"
echo ""
echo "🚀 Happy trading!"