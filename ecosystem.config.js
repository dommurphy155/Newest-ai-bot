module.exports = {
  apps: [{
    name: 'ai-trading-bot',
    script: 'main.py',
    interpreter: '/usr/bin/python3.8',
    cwd: '/home/ubuntu/Newest-ai-bot',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/workspace',
      PYTHONUNBUFFERED: '1',
      PYTHON_VERSION: '3.8.10',
      UBUNTU_VERSION: '20.04',
      LC_ALL: 'C.UTF-8',
      LANG: 'C.UTF-8'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000,
    kill_timeout: 5000,
    wait_ready: true,
    listen_timeout: 8000,
    exec_mode: 'fork',
    increment_var: 'PORT',
    combine_logs: true,
    force: true
  }]
};