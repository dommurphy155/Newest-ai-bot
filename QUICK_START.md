# 🚀 Quick Start - AI Trading Bot (Ubuntu 20.04)

## ⚡ 5-Minute Setup

### 1. Configure API Keys
```bash
nano config.py
```
Replace these lines with your real credentials:
```python
oanda_api_key: str = "your_actual_oanda_key"
oanda_account_id: str = "your_actual_account_id"  
telegram_bot_token: str = "your_actual_bot_token"
telegram_chat_id: str = "your_actual_chat_id"
```

### 2. Deploy Everything
```bash
./deploy_optimized.sh
```

### 3. Start Trading
```bash
sudo systemctl start ai-trading-bot
sudo systemctl status ai-trading-bot
```

### 4. Monitor
```bash
./monitor.sh
tail -f logs/bot.log
```

## 🔧 Environment Variables Alternative
Instead of editing config.py, you can export:
```bash
export OANDA_API_KEY='your_key'
export OANDA_ACCOUNT_ID='your_account'
export TELEGRAM_BOT_TOKEN='your_token'
export TELEGRAM_CHAT_ID='your_chat_id'
```

## ✅ System Requirements Met
- ✅ Ubuntu 20.04
- ✅ Python 3.8.10
- ✅ 0.6GB RAM optimized
- ✅ All dependencies compatible
- ✅ Memory usage ~100-200MB
- ✅ Auto-cleanup every 3.5 days

## 🎉 You're Ready to Trade!