#!/bin/bash

# Enhanced Ubuntu Setup Script for AI Trading Bot
# Lightweight deployment for Ubuntu 20.04+ with Python 3.8+

set -e  # Exit on any error

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system packages
print_status "📦 Updating Ubuntu packages..."
sudo apt update -y
sudo apt upgrade -y

# Install required system packages
print_status "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

print_success "System packages installed successfully"

# Create virtual environment
print_status "🐍 Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

print_success "Virtual environment created and activated"

# Upgrade pip and install requirements
print_status "📋 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_status "📁 Creating project directories..."
mkdir -p logs data

print_success "Project directories created"

# Set up systemd service file
print_status "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/trading-bot.service > /dev/null << EOF
[Unit]
Description=AI Trading Bot
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

sudo systemctl daemon-reload
print_success "Systemd service created"

# Set permissions
print_status "🔐 Setting file permissions..."
chmod +x *.py
chmod 755 *.sh

print_success "File permissions set"

# Final instructions
print_success "🎉 Setup completed successfully!"
echo ""
echo "📋 NEXT STEPS:"
echo "============================================"
echo ""
echo "1. Export your API credentials to the terminal:"
echo "   export OANDA_API_KEY='your_oanda_api_key'"
echo "   export OANDA_ACCOUNT_ID='your_account_id'"
echo "   export TELEGRAM_BOT_TOKEN='your_bot_token'"
echo "   export TELEGRAM_CHAT_ID='your_chat_id'"
echo "   export OANDA_ENVIRONMENT='practice'  # or 'live'"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Test the configuration:"
echo "   python3 validate_setup.py"
echo ""
echo "4. Start the bot:"
echo "   python3 main.py"
echo ""
echo "5. Or use systemd (run as service):"
echo "   sudo systemctl enable trading-bot"
echo "   sudo systemctl start trading-bot"
echo "   sudo systemctl status trading-bot"
echo ""
print_success "Happy trading! 🚀"