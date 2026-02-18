import os
import sys
import subprocess
try:
    import telegram
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot"])

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = 'your_bot_token'

async def now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]: return
    member = await chat.get_member(update.effective_user.id)
    if member.status not in ["creator", "administrator"]: return
    context.chat_data['clean_mode'] = True
    await update.message.reply_text("تم التفعيل.")

async def ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('clean_mode') is not True: return
    chat = update.effective_chat
    user = update.effective_user
    try:
        member = await chat.get_member(user.id)
        if member.status not in ["creator", "administrator"]:
            await chat.ban_member(user.id)
    except: pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('now', now_command))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, ban_handler))
    app.run_polling()
