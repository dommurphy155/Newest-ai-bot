module.exports = {
  apps: [
    {
      name: "ai-trading-bot",
      script: "main.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/ubuntu/Newest-ai-bot",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      env: {
        HUGGING_FACE_TOKEN: "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",
        TELEGRAM_BOT_TOKEN: "7874560450:AAH-Bmu1GJTVjwRM7jounms9FFYfC4EbVBQ",
        TELEGRAM_CHAT_ID: "8038953791",
        OANDA_API: "e02c6cecb654c12d7874d8d5a7a912cc-463d0c7414dbc13e09ce5fbd4d309e02",
        OANDA_ACCOUNT_ID: "101-004-31152935-001"
      },
      error_file: "./logs/pm2-error-0.log",
      out_file: "./logs/pm2-out-0.log",
      merge_logs: true,
      time: true
    }
  ]
};
