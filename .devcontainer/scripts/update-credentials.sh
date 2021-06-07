#!/bin/bash

export $(egrep -v '^#' /workspace/.env | xargs)

echo "telegram:
    access_token: \"$TELEGRAM_BOT_TOKEN\"
    verify: \"$TELEGRAM_BOT_USERNAME\"
    webhook_url: \"https://$(curl --silent --show-error http://localhost:4040/api/tunnels | sed -nE 's/.*public_url":"https:..([^"]*).*/\1/p')/webhooks/telegram/webhook\"
" > /app/credentials.yml
