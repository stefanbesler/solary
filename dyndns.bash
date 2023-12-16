#!/bin/bash
set -e

HOSTNAME=""
PASSWORD=""
ENDPOINT="https://dynamicdns.key-systems.net/update.php?hostname=${HOSTNAME}&password=${PASSWORD}"
EXTERNAL_IP=$(curl -s ifconfig.me)

if [ -z "$EXTERNAL_IP" ]; then
  echo "Failed to get external IP address."
  exit 1
fi

URL="${ENDPOINT}&ip=${EXTERNAL_IP}"
curl -s "${URL}" > /dev/null

echo "Update dyndns with $EXTERNAL_IP at: $(date)"
exit 0

