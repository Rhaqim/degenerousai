#!/usr/bin/env bash

# Install supervisord
apt-get update
apt-get install -y supervisor

# Run supervisord
supervisord -c /etc/supervisor/supervisord.conf

# Create fastapi.conf in /etc/supervisor/conf.d/
cat <<EOL > /etc/supervisor/conf.d/fastapi.conf
[program:fastapi]
command=/root/.local/bin/poetry run python src/degenerousai/main.py
autostart=true
autorestart=true
stderr_logfile=/var/log/fastapi.err.log
stdout_logfile=/var/log/fastapi.out.log
environment=PATH="/root/.local/bin:%(ENV_PATH)s"
EOL

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# export poetry to path
export PATH="/root/.local/bin:$PATH"