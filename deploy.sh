#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying AI Trading Bot (Ubuntu 20.04 / Python 3.8+)${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check Ubuntu version
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ "$VERSION_ID" != "20.04" ]]; then
        print_warning "This script is optimized for Ubuntu 20.04. Current version: $VERSION_ID"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_warning "Cannot detect Ubuntu version"
fi

# Update system packages
print_status "Updating system packages..."
sudo apt-get update -qq

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-venv \
    python3-pip \
    build-essential \
    curl \
    git \
    software-properties-common \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_status "Python version: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [[ -d "venv" ]]; then
    print_warning "Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Upgrade pip and essential packages
print_status "Upgrading pip and essential packages..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python dependencies..."
if [[ ! -f "requirements.txt" ]]; then
    print_error "requirements.txt not found!"
    exit 1
fi

pip install -r requirements.txt

# Verify critical imports
print_status "Verifying critical imports..."
python3 -c "
import sys
try:
    import telegram
    import oandapyV20
    import aiohttp
    import asyncio
    import logging
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Set up logging
print_status "Setting up logging..."
touch logs/bot.log
touch logs/error.log

# Create systemd service file for PM2 alternative
print_status "Creating systemd service file..."
cat > trading-bot.service << EOF
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
StandardOutput=append:$(pwd)/logs/bot.log
StandardError=append:$(pwd)/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service file created: trading-bot.service"

# Create PM2 ecosystem file
print_status "Creating PM2 ecosystem file..."
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'ai-trading-bot',
    script: './venv/bin/python',
    args: 'main.py',
    cwd: '$(pwd)',
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '512M',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '$(pwd)',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/error.log',
    out_file: './logs/bot.log',
    log_file: './logs/combined.log',
    time: true,
    restart_delay: 5000,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
EOF

print_status "PM2 ecosystem file created: ecosystem.config.js"

# Create startup script
print_status "Creating startup script..."
cat > start_bot.sh << 'EOF'
#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check if all required environment variables are set
required_vars=("TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID" "OANDA_API_KEY" "OANDA_ACCOUNT_ID")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "❌ Missing required environment variables:"
    printf '   %s\n' "${missing_vars[@]}"
    echo ""
    echo "Please export the required variables:"
    for var in "${missing_vars[@]}"; do
        echo "export $var=your_value"
    done
    exit 1
fi

echo "🚀 Starting AI Trading Bot..."
exec python main.py
EOF

chmod +x start_bot.sh
print_status "Startup script created: start_bot.sh"

# Create stop script
print_status "Creating stop script..."
cat > stop_bot.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping AI Trading Bot..."

# Stop PM2 if running
if command -v pm2 &> /dev/null; then
    pm2 stop ai-trading-bot 2>/dev/null || true
fi

# Stop systemd service if running
if systemctl is-active --quiet trading-bot 2>/dev/null; then
    sudo systemctl stop trading-bot
fi

# Kill any remaining Python processes
pkill -f "python.*main.py" 2>/dev/null || true

echo "✅ Bot stopped"
EOF

chmod +x stop_bot.sh
print_status "Stop script created: stop_bot.sh"

# Create environment template
print_status "Creating environment template..."
cat > .env.template << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# OANDA Trading API Configuration
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here

# Optional: Hugging Face Token for AI models
HF_TOKEN=your_huggingface_token_here

# Optional: Environment
ENVIRONMENT=production
EOF

print_status "Environment template created: .env.template"

# Final checks
print_status "Running final checks..."

# Check if main.py exists and is executable
if [[ ! -f "main.py" ]]; then
    print_error "main.py not found!"
    exit 1
fi

# Test Python syntax
if ! python3 -m py_compile main.py; then
    print_error "Syntax error in main.py!"
    exit 1
fi

print_status "All checks passed!"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Export your environment variables:"
echo "   export TELEGRAM_BOT_TOKEN=your_token"
echo "   export TELEGRAM_CHAT_ID=your_chat_id"
echo "   export OANDA_API_KEY=your_api_key"
echo "   export OANDA_ACCOUNT_ID=your_account_id"
echo ""
echo "2. Start the bot using one of these methods:"
echo "   • Direct: ./start_bot.sh"
echo "   • PM2: pm2 start ecosystem.config.js"
echo "   • Systemd: sudo systemctl start trading-bot"
echo ""
echo "3. Monitor logs:"
echo "   • tail -f logs/bot.log"
echo "   • tail -f logs/error.log"
echo ""
echo -e "${BLUE}Bot is ready to run!${NC}"