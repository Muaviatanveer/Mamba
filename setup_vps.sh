#!/bin/bash
echo "=================================================="
echo "  🐍 Setting Up Mamba Self-Hosted Cloud on VPS    "
echo "=================================================="

# 1. Install C++ Compiler, SQLite, Git, Python
sudo apt-get update -y
sudo apt-get install -y clang libsqlite3-dev git python3 python3-pip python3-venv

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install lark

# 3. Make mamba CLI executable
chmod +x mamba

# 4. Open Firewall Ports 80, 8000, 8081 for Global Internet Traffic
sudo ufw allow 80/tcp 2>/dev/null
sudo ufw allow 8000/tcp 2>/dev/null
sudo ufw allow 8081/tcp 2>/dev/null

echo "=================================================="
echo "✨ Mamba Cloud VPS Setup Complete!"
echo "=================================================="
