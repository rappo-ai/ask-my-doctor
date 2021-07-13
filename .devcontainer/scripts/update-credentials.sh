#!/bin/bash

export $(egrep -v '^#' /app/.env | xargs)

echo "connectors.telegram.TelegramInput:
    access_token: \"$TELEGRAM_BOT_TOKEN\"
    verify: \"$TELEGRAM_BOT_USERNAME\"
    webhook_url: \"https://$(curl --silent --show-error http://localhost:4040/api/tunnels | sed -nE 's/.*public_url":"https:..([^"]*).*/\1/p')/webhooks/telegram/webhook\"
    host_url: \"https://$(curl --silent --show-error http://localhost:4040/api/tunnels | sed -nE 's/.*public_url":"https:..([^"]*).*/\1/p')\"" > /app/dataset/credentials.yml
