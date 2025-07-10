#!/bin/bash
set -e

# AI Trading Bot Startup Script
# Compatible with PM2 and systemd

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting AI Trading Bot from $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run deploy.sh first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Verify Python and dependencies
echo "🔍 Verifying Python installation..."
python3 --version

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set environment variables for logging
export PYTHONUNBUFFERED=1
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Check environment variables (optional check)
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN not set. Make sure to export it before running."
fi

if [ -z "$OANDA_API_KEY" ]; then
    echo "⚠️  OANDA_API_KEY not set. Make sure to export it before running."
fi

# Handle signals gracefully
trap 'echo "🛑 Received shutdown signal, stopping bot..."; exit 0' SIGINT SIGTERM

# Start the bot
echo "✅ Starting AI Trading Bot..."
echo "📝 Logs will be written to bot.log and logs/"
echo "🔄 Bot is running... Press Ctrl+C to stop"

# Execute the main Python script
exec python3 main.py