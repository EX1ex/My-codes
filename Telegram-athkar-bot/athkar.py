import subprocess, sys
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import telegram
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, CallbackContext
except ImportError:
    install("python-telegram-bot==13.17")
    import telegram
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, CallbackContext

import random
from datetime import datetime

TOKEN = "your_bot_token"
GROUP_IDS_FILE = "groups.txt"
ATHKAR_FILE = "athkar.txt"
LAST_SENT = {}

def load_athkar():
    if not os.path.exists(ATHKAR_FILE):
        return ["سبحان الله", "الحمد لله", "لا إله إلا الله", "الله أكبر"]
    with open(ATHKAR_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    athkar, temp, inside = [], "", False
    for c in content:
        if c == "{": inside, temp = True, ""
        elif c == "}": 
            if inside: athkar.append(temp.strip())
            inside = False
        elif inside: temp += c
    return athkar if athkar else ["سبحان الله"]

def save_group_id(group_id):
    try: ids = open(GROUP_IDS_FILE, "r", encoding="utf-8").read().splitlines()
    except FileNotFoundError: ids = []
    if str(group_id) not in ids:
        with open(GROUP_IDS_FILE, "a", encoding="utf-8") as f:
            f.write(str(group_id) + "\n")

def start(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type == "private":
        update.message.reply_text("قم باضافة البوت لمجموعه لبدء استخدامه")
    else:
        update.message.reply_text("تم تفعيل البوت في هذه المجموعه")
        save_group_id(chat.id)

def get_random_zekr(athkar_list, last_sent_list):
    available = [z for z in athkar_list if z not in last_sent_list]
    if not available: last_sent_list.clear(); available = athkar_list
    chosen = random.choice(available)
    last_sent_list.append(chosen)
    if len(last_sent_list) > 10: last_sent_list.pop(0)
    return chosen

def scheduled_athkar(context: CallbackContext):
    athkar_list = load_athkar()
    try: group_ids = open(GROUP_IDS_FILE, "r", encoding="utf-8").read().splitlines()
    except FileNotFoundError: group_ids = []
    for gid in group_ids:
        try:
            gid_int = int(gid)
            if gid_int not in LAST_SENT: LAST_SENT[gid_int] = []
            zekr = get_random_zekr(athkar_list, LAST_SENT[gid_int])
            context.bot.send_message(chat_id=gid_int, text=zekr)
        except: continue

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    job_queue = updater.job_queue
    job_queue.run_repeating(scheduled_athkar, interval=3600, first=10)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
