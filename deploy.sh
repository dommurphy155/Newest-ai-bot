#!/bin/bash

# AI Trading Bot v3.0 - Production Deployment Script
# Compatible with Ubuntu 20.04, Python 3.8+, and PM2
# Optimized for Maximum Profit Generation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_NAME="ai-trading-bot-v3"
BOT_DIR="$(pwd)"
VENV_DIR="$BOT_DIR/venv"
LOG_DIR="$BOT_DIR/logs"
DATA_DIR="$BOT_DIR/data"
PYTHON_VERSION="3.8"

# Print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VER detected (compatible)"
            PYTHON_CMD="python3"
        else
            print_error "Python $PYTHON_VER detected (requires 3.8+)"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt-get update -qq
    
    # Install essential packages
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        curl \
        wget \
        git \
        pkg-config \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        libblas-dev \
        liblapack-dev \
        gfortran \
        sqlite3 \
        libsqlite3-dev \
        redis-server \
        supervisor
    
    print_success "System dependencies installed"
}

# Function to install Node.js and PM2
install_pm2() {
    print_status "Installing Node.js and PM2..."
    
    if ! command_exists node; then
        # Install Node.js LTS
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    if ! command_exists pm2; then
        sudo npm install -g pm2
        # Setup PM2 startup script
        sudo pm2 startup systemd -u $USER --hp $HOME
    fi
    
    print_success "PM2 installed and configured"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [ -d "$VENV_DIR" ]; then
        print_warning "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create new virtual environment
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Virtual environment created"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install dependencies with optimizations
    pip install --no-cache-dir -r requirements.txt
    
    # Install additional performance packages
    pip install --no-cache-dir \
        uvloop \
        orjson \
        cchardet \
        aiodns
    
    print_success "Python dependencies installed"
}

# Function to create directories
create_directories() {
    print_status "Creating required directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$BOT_DIR/backups"
    mkdir -p "$BOT_DIR/config"
    
    # Set permissions
    chmod 755 "$LOG_DIR" "$DATA_DIR"
    
    print_success "Directories created"
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if [ ! -f "$BOT_DIR/.env" ]; then
        cat > "$BOT_DIR/.env" << EOF
# AI Trading Bot v3.0 Configuration
# REQUIRED: Set these values before deployment

# OANDA Configuration
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_ENVIRONMENT=practice

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Optional: Hugging Face Token for AI features
HF_TOKEN=your_huggingface_token_here

# Performance Settings
MAX_WORKERS=4
LOG_LEVEL=INFO
SCAN_INTERVAL=5
NEWS_INTERVAL=10

# Risk Management
MAX_RISK_PER_TRADE=0.01
MAX_DAILY_RISK=0.05
MAX_POSITIONS=5

EOF
        print_warning "Created .env file - Please configure your API keys!"
    else
        print_success "Environment file already exists"
    fi
}

# Function to create PM2 ecosystem file
create_pm2_config() {
    print_status "Creating PM2 configuration..."
    
    cat > "$BOT_DIR/ecosystem.config.js" << EOF
module.exports = {
  apps: [{
    name: '$BOT_NAME',
    script: '$VENV_DIR/bin/python',
    args: 'main.py',
    cwd: '$BOT_DIR',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '$BOT_DIR',
      PYTHONUNBUFFERED: '1'
    },
    error_file: '$LOG_DIR/pm2-error.log',
    out_file: '$LOG_DIR/pm2-out.log',
    log_file: '$LOG_DIR/pm2-combined.log',
    time: true,
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000
  }]
};
EOF
    
    print_success "PM2 configuration created"
}

# Function to setup systemd service (alternative to PM2)
create_systemd_service() {
    print_status "Creating systemd service as backup..."
    
    sudo tee /etc/systemd/system/$BOT_NAME.service > /dev/null << EOF
[Unit]
Description=AI Trading Bot v3.0
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$BOT_DIR
Environment=PYTHONPATH=$BOT_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$VENV_DIR/bin/python main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$BOT_NAME

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    print_success "Systemd service created"
}

# Function to setup log rotation
setup_logrotate() {
    print_status "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/$BOT_NAME > /dev/null << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        pm2 reload $BOT_NAME > /dev/null 2>&1 || true
    endscript
}
EOF
    
    print_success "Log rotation configured"
}

# Function to check environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    source "$BOT_DIR/.env" 2>/dev/null || true
    
    missing_vars=()
    
    if [ -z "$OANDA_API_KEY" ] || [ "$OANDA_API_KEY" = "your_oanda_api_key_here" ]; then
        missing_vars+=("OANDA_API_KEY")
    fi
    
    if [ -z "$OANDA_ACCOUNT_ID" ] || [ "$OANDA_ACCOUNT_ID" = "your_oanda_account_id_here" ]; then
        missing_vars+=("OANDA_ACCOUNT_ID")
    fi
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
        missing_vars+=("TELEGRAM_BOT_TOKEN")
    fi
    
    if [ -z "$TELEGRAM_CHAT_ID" ] || [ "$TELEGRAM_CHAT_ID" = "your_telegram_chat_id_here" ]; then
        missing_vars+=("TELEGRAM_CHAT_ID")
    fi
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_warning "Please edit $BOT_DIR/.env and set the required values"
        return 1
    fi
    
    print_success "All required environment variables are set"
    return 0
}

# Function to test the bot
test_bot() {
    print_status "Testing bot configuration..."
    
    source "$VENV_DIR/bin/activate"
    cd "$BOT_DIR"
    
    # Test import and basic functionality
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from config import config
    from bot import EnhancedTradingBot
    from trader import AdvancedTrader
    from scraper import AdvancedMarketIntelligence
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"; then
        print_success "Bot configuration test passed"
        return 0
    else
        print_error "Bot configuration test failed"
        return 1
    fi
}

# Function to start the bot
start_bot() {
    print_status "Starting AI Trading Bot v3.0..."
    
    cd "$BOT_DIR"
    
    # Stop existing instance if running
    pm2 stop $BOT_NAME 2>/dev/null || true
    pm2 delete $BOT_NAME 2>/dev/null || true
    
    # Start with PM2
    pm2 start ecosystem.config.js
    pm2 save
    
    # Show status
    sleep 3
    pm2 status $BOT_NAME
    
    print_success "Bot started successfully!"
    print_status "Monitor logs with: pm2 logs $BOT_NAME"
    print_status "Check status with: pm2 status"
    print_status "Stop bot with: pm2 stop $BOT_NAME"
}

# Function to show monitoring commands
show_monitoring() {
    print_status "Monitoring Commands:"
    echo "  pm2 logs $BOT_NAME           # View live logs"
    echo "  pm2 status                   # Check status"
    echo "  pm2 restart $BOT_NAME        # Restart bot"
    echo "  pm2 stop $BOT_NAME           # Stop bot"
    echo "  pm2 monit                    # Real-time monitoring"
    echo ""
    echo "  tail -f $LOG_DIR/bot.log     # View application logs"
    echo "  systemctl status $BOT_NAME   # Check systemd service"
    echo ""
    print_status "Configuration files:"
    echo "  $BOT_DIR/.env                # Environment variables"
    echo "  $BOT_DIR/ecosystem.config.js # PM2 configuration"
}

# Main deployment function
main() {
    clear
    echo "=========================================="
    echo "🚀 AI Trading Bot v3.0 Deployment Script"
    echo "   Optimized for Maximum Profit!"
    echo "=========================================="
    echo ""
    
    print_status "Starting deployment process..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root!"
        exit 1
    fi
    
    # Check operating system
    if ! grep -q "Ubuntu" /etc/os-release; then
        print_warning "This script is optimized for Ubuntu 20.04"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Change to bot directory
    cd "$BOT_DIR"
    
    # Run deployment steps
    check_python_version
    install_system_deps
    install_pm2
    create_directories
    setup_venv
    install_python_deps
    setup_environment
    create_pm2_config
    create_systemd_service
    setup_logrotate
    
    # Test configuration
    if check_env_vars && test_bot; then
        start_bot
        show_monitoring
        
        echo ""
        print_success "🎯 AI Trading Bot v3.0 deployed successfully!"
        print_success "💰 Ready for maximum profit generation!"
        echo ""
    else
        print_error "Deployment completed with issues"
        print_warning "Please fix the configuration and run: pm2 start ecosystem.config.js"
    fi
}

# Handle command line arguments
case "${1:-}" in
    "start")
        start_bot
        ;;
    "stop")
        pm2 stop $BOT_NAME
        ;;
    "restart")
        pm2 restart $BOT_NAME
        ;;
    "status")
        pm2 status $BOT_NAME
        ;;
    "logs")
        pm2 logs $BOT_NAME
        ;;
    "test")
        source "$VENV_DIR/bin/activate"
        test_bot
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status|logs|test]"
        echo "  start   - Start the bot"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Show bot status"
        echo "  logs    - Show bot logs"
        echo "  test    - Test configuration"
        echo ""
        echo "Run without arguments for full deployment"
        ;;
esac