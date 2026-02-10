#!/usr/bin/env bash

set -e

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# export poetry to path
export PATH="/root/.local/bin:$PATH"

# Install supervisord
apt-get update
apt-get install -y supervisor

# Create degenerousai.conf in /etc/supervisor/conf.d/
cat <<EOL > /etc/supervisor/conf.d/degenerousai.conf
[program:degenerousai]
command=/root/.local/bin/poetry run python src/degenerousai/main.py
directory=/workspace/degenerousai
autostart=true
autorestart=true
stderr_logfile=/var/log/degenerousai.err.log
stdout_logfile=/var/log/degenerousai.out.log
environment=PATH="/root/.local/bin:%(ENV_PATH)s"
EOL

# Run supervisord
# supervisord -c /etc/supervisor/supervisord.conf
supervisord

# Reload supervisord to apply changes
supervisorctl reread
supervisorctl update

# Start the degenerousai program
supervisorctl start degenerousai

# Wait for the degenerousai program to start
sleep 5

# Check if the degenerousai program is running
if supervisorctl status degenerousai | grep -q "RUNNING"; then
    echo "Degenerousai program is running"
else
    echo "Degenerousai program is not running"
    exit 1
fi