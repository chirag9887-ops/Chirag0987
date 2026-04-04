#!/bin/bash

# PRIME DDOS BOT - Auto Installer
# Created by @PRIMEXARMY

echo "🔥 PRIME DDOS BOT INSTALLER 🔥"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update system
echo "[1/6] Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "[2/6] Installing dependencies..."
apt install -y python3 python3-pip git gcc make build-essential screen htop

# Install Python packages
echo "[3/6] Installing Python packages..."
pip3 install -r requirements.txt

# Compile attack tool
echo "[4/6] Compiling attack tool..."
gcc -O3 -pthread -o bgmi bgmi.c
chmod +x bgmi

# Create start script
echo "[5/6] Creating start script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd /root/prime-ddos
echo "Starting PRIME DDOS BOT..."
screen -dmS prime-bot python3 bot.py
echo "Bot started in screen session 'prime-bot'"
echo "View logs: screen -r prime-bot"
EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
pkill -f "python3 bot.py"
screen -X -S prime-bot quit
echo "PRIME DDOS BOT stopped"
EOF

chmod +x stop.sh

echo "[6/6] Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📌 Next steps:"
echo "1. Edit bot.py and add your BOT_TOKEN"
echo "2. Run: ./start.sh"
echo "3. Check: screen -r prime-bot"
echo ""
echo "📊 Commands:"
echo "  ./start.sh  - Start bot"
echo "  ./stop.sh   - Stop bot"
echo "  screen -r prime-bot - View logs"
echo ""
echo "👑 Created by @PRIMEXARMY"