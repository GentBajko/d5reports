#!/bin/bash

REMOTE_USER="root"
REMOTE_HOST="156.67.27.196"
REMOTE_PORT=22

REMOTE_APP_DIR="/root/d5reports"


SSH_CMD="ssh -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

REMOTE_COMMANDS="
    set -e  # Exit immediately if a command exits with a non-zero status
    cd ${REMOTE_APP_DIR}

    echo 'Stopping fastapi service...'
    sudo systemctl stop fastapi

    echo 'Reloading systemd daemon...'
    sudo systemctl daemon-reload

    echo 'Restarting fastapi service...'
    sudo systemctl restart fastapi

    echo 'Restart completed successfully.'
"

echo "Connecting to ${REMOTE_HOST}..."
$SSH_CMD "${REMOTE_COMMANDS}"
