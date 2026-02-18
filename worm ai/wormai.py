import sys
import subprocess
import importlib
import json
import os
import random
import asyncio
import re
from datetime import datetime

def install_deps():
    for pkg in ['python-telegram-bot', 'huggingface_hub']:
        try:
            importlib.import_module(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

install_deps()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

TELEGRAM_TOKEN = "your_bot_token"
OWNER_ID = 0000000000
CHANNEL_ID = "@your_channel"
CHANNEL_URL = "https://t.me/your_channel"

HF_TOKENS = ["your_huggingface_token_1", "your_huggingface_token_2"]

MODEL_ID = "deepseek-ai/DeepSeek-R1" 
USERS_FILE = "users.json"
SYSTEM_FILE = "worm_system.txt"
COOLDOWN_SECONDS = 60 

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID: return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("اضغط هنا للاشتراك 📢", url=CHANNEL_URL)]])
    await update.message.reply_text(
        "⚠️ يجب عليك الاشتراك في القناة أولاً لاستخدام البوت!",
        reply_markup=keyboard
    )
    return False

def get_system_prompt():
    if not os.path.exists(SYSTEM_FILE):
        with open(SYSTEM_FILE, "w", encoding="utf-8") as f:
            f.write("You are DeepSeek-R1. Respond directly.")
    with open(SYSTEM_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_db():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_thought(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def get_random_client():
    token = random.choice(HF_TOKENS)
    return InferenceClient(api_key=token)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    if str(user.id) not in db:
        db[str(user.id)] = {"name": user.full_name, "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        save_db(db)
    
    msg = (
        f"مرحباً بك {user.first_name} في بوت Worm AI v3 🐍\n\n"
        f"أنا أعمل بنموذج DeepSeek-R1 المتطور.\n"
        f"يمكنك سؤالي عن أي شيء وسأجيبك بدقة."
    )
    await update.message.reply_text(msg)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    count = len(db)
    await update.message.reply_text(f"📊 إحصائيات البوت:\nعدد المستخدمين: {count}")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if not await check_sub(update, context): return

    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id not in db:
        db[user_id] = {"name": update.effective_user.full_name, "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        save_db(db)
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        sys_p = get_system_prompt()
        messages = [{"role": "system", "content": sys_p}, {"role": "user", "content": update.message.text}]
        
        client = get_random_client()
        full_res = ""
        completion = client.chat.completions.create(model=MODEL_ID, messages=messages, max_tokens=2000, stream=True)
        
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
        
        final_answer = clean_thought(full_res)
        
        if final_answer:
            await update.message.reply_text(final_answer)
        elif full_res:
            await update.message.reply_text("عذراً، لم أستطع تكوين رد مباشر حالياً.")
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ فني: {str(e)}")

if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()
