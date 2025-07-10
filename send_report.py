import os
import telegram

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env variables")

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(text: str):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)