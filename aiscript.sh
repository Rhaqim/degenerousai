#!/usr/bin/env bash

set -e

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# export poetry to path
export PATH="/root/.local/bin:$PATH"

# Install supervisord
apt-get update
apt-get install -y supervisor

# Create fastapi.conf in /etc/supervisor/conf.d/
cat <<EOL > /etc/supervisor/conf.d/fastapi.conf
[program:fastapi]
command=/root/.local/bin/poetry run python src/degenerousai/main.py
directory=/workspace/degenerousai
autostart=true
autorestart=true
stderr_logfile=/var/log/fastapi.err.log
stdout_logfile=/var/log/fastapi.out.log
environment=PATH="/root/.local/bin:%(ENV_PATH)s"
EOL

# Run supervisord
# supervisord -c /etc/supervisor/supervisord.conf
supervisord

# Reload supervisord to apply changes
supervisorctl reread
supervisorctl update

# Start the fastapi program
supervisorctl start fastapi

# Wait for the fastapi program to start
sleep 5

# Check if the fastapi program is running
if supervisorctl status fastapi | grep -q "RUNNING"; then
    echo "FastAPI program is running"
else
    echo "FastAPI program is not running"
    exit 1
fi