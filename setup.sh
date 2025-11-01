#!/usr/bin/env bash
set -e

# Update & minimal packages
sudo apt update
sudo apt install -y build-essential python3-venv python3-dev gcc libpcap-dev tcpdump

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install python deps
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate virtualenv with: source .venv/bin/activate"
