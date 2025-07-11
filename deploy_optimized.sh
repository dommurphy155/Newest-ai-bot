#!/bin/bash

# Optimized AI Trading Bot Deployment Script
# Ubuntu 20.04 + Python 3.8.10 + Memory Optimized for 0.6GB systems
# Author: AI Assistant
# Version: 3.0

set -e

echo "🚀 AI Trading Bot - Optimized Deployment for Ubuntu 20.04"
echo "====================================================="

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu 20.04" /etc/os-release; then
        warn "Not Ubuntu 20.04, but proceeding anyway..."
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    if [[ ! "$PYTHON_VERSION" =~ ^3\.8\. ]]; then
        error "Python 3.8.x required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    # Check memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -lt 1 ]; then
        warn "Low memory detected: ${MEMORY_GB}GB. Optimizing for minimal usage..."
    fi
    
    log "✅ System check passed: Python $PYTHON_VERSION, Memory: ${MEMORY_GB}GB"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libssl-dev \
        libffi-dev \
        sqlite3 \
        curl \
        wget
    
    log "✅ System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        rm -rf venv
    fi
    
    # Create new virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip for better dependency resolution
    pip install --upgrade pip==21.3.1
    
    # Install wheel for faster compilation
    pip install wheel==0.37.1
    
    log "✅ Virtual environment created"
}

# Install Python packages
install_packages() {
    log "Installing Python packages (memory-optimized versions)..."
    
    source venv/bin/activate
    
    # Install packages one by one to handle potential conflicts
    pip install --no-cache-dir -r requirements.txt
    
    log "✅ Python packages installed"
}

# Configure system for low memory
optimize_system() {
    log "Optimizing system for low memory usage..."
    
    # Create swap file if memory is low
    MEMORY_MB=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_MB" -lt 1024 ]; then
        log "Creating swap file for low memory system..."
        
        if [ ! -f /swapfile ]; then
            sudo fallocate -l 1G /swapfile
            sudo chmod 600 /swapfile
            sudo mkswap /swapfile
            sudo swapon /swapfile
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        fi
    fi
    
    # Set memory limits for the bot
    echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
    echo "vm.vfs_cache_pressure=50" | sudo tee -a /etc/sysctl.conf
    
    log "✅ System optimized for low memory"
}

# Setup directories and permissions
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p logs data backups
    chmod 755 logs data backups
    
    # Set up log rotation to prevent disk space issues
    sudo tee /etc/logrotate.d/trading-bot > /dev/null <<EOF
/workspace/logs/*.log {
    daily
    missingok
    rotate 3
    compress
    delaycompress
    notifempty
    copytruncate
    maxsize 5M
}
EOF
    
    log "✅ Directories and permissions set"
}

# Create systemd service
create_service() {
    log "Creating systemd service..."
    
    sudo tee /etc/systemd/system/ai-trading-bot.service > /dev/null <<EOF
[Unit]
Description=AI Trading Bot - Memory Optimized
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$(pwd)
Environment=PYTHONUNBUFFERED=1
ExecStart=$(pwd)/venv/bin/python3 main.py
Restart=always
RestartSec=30
StandardOutput=append:$(pwd)/logs/service.log
StandardError=append:$(pwd)/logs/service-error.log

# Memory and CPU limits for low-resource systems
MemoryMax=400M
MemoryHigh=300M
CPUQuota=80%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$(pwd)

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable ai-trading-bot
    
    log "✅ Systemd service created and enabled"
}

# Validate installation
validate_installation() {
    log "Validating installation..."
    
    # Test imports
    source venv/bin/activate
    
    if ! python3 -c "import main; print('✅ Main imports successful')"; then
        error "Import validation failed"
        exit 1
    fi
    
    # Test database creation
    if ! python3 -c "
from database import Database
import asyncio
async def test_db():
    db = Database()
    await db.initialize()
    print('✅ Database initialization successful')
asyncio.run(test_db())
"; then
        error "Database validation failed"
        exit 1
    fi
    
    log "✅ Installation validation passed"
}

# Setup monitoring script
create_monitoring() {
    log "Creating monitoring script..."
    
    cat > monitor.sh <<'EOF'
#!/bin/bash

# Simple monitoring script for the trading bot
echo "=== AI Trading Bot Status ==="
echo "Date: $(date)"
echo ""

# Check service status
echo "Service Status:"
systemctl is-active ai-trading-bot
echo ""

# Check memory usage
echo "Memory Usage:"
ps aux | grep -E "(python3|main.py)" | grep -v grep | awk '{print "CPU: " $3 "%, Memory: " $4 "%, PID: " $2}'
echo ""

# Check disk space
echo "Disk Usage:"
df -h . | tail -1 | awk '{print "Used: " $3 "/" $2 " (" $5 ")"}'
echo ""

# Check recent logs
echo "Recent Logs (last 10 lines):"
tail -10 logs/bot.log 2>/dev/null || echo "No logs yet"
echo ""

# Check database size
if [ -f "data/trading_bot.db" ]; then
    DB_SIZE=$(du -h data/trading_bot.db | cut -f1)
    echo "Database Size: $DB_SIZE"
fi
EOF
    
    chmod +x monitor.sh
    
    log "✅ Monitoring script created (run ./monitor.sh)"
}

# Cleanup function
cleanup_old_installations() {
    log "Cleaning up old installations..."
    
    # Stop any running services
    sudo systemctl stop ai-trading-bot 2>/dev/null || true
    
    # Clean old pip cache
    pip cache purge 2>/dev/null || true
    
    # Clean old logs (keep last 3 days)
    find logs -name "*.log" -mtime +3 -delete 2>/dev/null || true
    
    log "✅ Cleanup completed"
}

# Main deployment function
main() {
    echo ""
    log "Starting optimized deployment for Ubuntu 20.04 + Python 3.8.10"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        error "Do not run this script as root!"
        exit 1
    fi
    
    # Main deployment steps
    check_system
    cleanup_old_installations
    install_dependencies
    setup_python_env
    install_packages
    optimize_system
    setup_directories
    create_service
    validate_installation
    create_monitoring
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "====================================="
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure your API credentials in config.py:"
    echo "   nano config.py"
    echo ""
    echo "2. Start the service:"
    echo "   sudo systemctl start ai-trading-bot"
    echo ""
    echo "3. Check status:"
    echo "   sudo systemctl status ai-trading-bot"
    echo "   ./monitor.sh"
    echo ""
    echo "4. View logs:"
    echo "   tail -f logs/bot.log"
    echo ""
    echo "💾 Memory footprint: ~100-200MB"
    echo "⚡ Installation size: ~50MB"
    echo "🔧 Optimized for 0.6GB systems"
    echo ""
    echo "🚀 Happy trading!"
}

# Run main function
main "$@"