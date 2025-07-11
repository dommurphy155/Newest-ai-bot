module.exports = {
  apps: [{
    name: 'ai-trading-bot',
    script: 'main.py',
    interpreter: '/home/ubuntu/Newest-ai-bot/venv/bin/python',
    cwd: '/home/ubuntu/Newest-ai-bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
