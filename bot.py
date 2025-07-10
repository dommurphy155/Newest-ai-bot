import os
from telegram.ext import ApplicationBuilder

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.run_polling()
