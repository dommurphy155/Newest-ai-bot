#!/bin/bash
set -e

echo "🚀 Deploying AI Trading Bot (Ubuntu 20.04 / Python 3.8)"

# Check python3 and venv
if ! command -v python3 &>/dev/null; then
  echo "Python3 is not installed. Please install Python 3.8."
  exit 1
fi

if ! python3 -m venv venv 2>/dev/null; then
  echo "Installing python3.8-venv package..."
  sudo apt-get update
  sudo apt-get install -y python3.8-venv
  python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Deployment complete."
echo ""
echo "Before running the bot, export your secrets:"
echo "export HF_TOKEN=your_huggingface_token"
echo "export TELEGRAM_BOT_TOKEN=your_telegram_token"
echo "export TELEGRAM_CHAT_ID=your_telegram_chat_id"
echo "export OANDA_API_KEY=your_oanda_api_key"
echo "export OANDA_ACCOUNT_ID=your_oanda_account_id"
echo ""
echo "Then start bot with:"
echo "python3 main.py"