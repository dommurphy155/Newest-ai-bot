import os
from bot import run_bot

if __name__ == "__main__":
    print("🔥 Starting main.py")
    run_bot(
        huggingface_token=os.environ["HUGGINGFACE_TOKEN"],
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        telegram_chat_id=os.environ["TELEGRAM_CHAT_ID"],
        oanda_api_key=os.environ["OANDA_API_KEY"],
        oanda_account_id=os.environ["OANDA_ACCOUNT_ID"]
    )

