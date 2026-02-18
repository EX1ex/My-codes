import subprocess
import sys
import os

def install_requirements():
    try:
        import telethon
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "telethon", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

install_requirements()

import logging
from telethon import TelegramClient, events

API_ID = 0000000
API_HASH = 'your_api_hash'
SESSION_NAME = 'owner_session'
MEMORY_FILE = 'waiting_ids.txt'

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return set()
    with open(MEMORY_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_memory(ids_set):
    with open(MEMORY_FILE, 'w') as f:
        for user_id in ids_set:
            f.write(f"{user_id}\n")

waiting_list = load_memory()
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_incoming(event):
    user_id = str(event.chat_id)
    if user_id in waiting_list:
        return

    is_waiting = True
    welcome_msg_text = "مرحباً، أنا مشغول حالياً، سيرد عليك من المالك قريباً"
    
    try:
        async for msg in client.iter_messages(event.chat_id, limit=20):
            if msg.out and msg.text == welcome_msg_text:
                is_waiting = False
                break
    except Exception:
        pass

    if is_waiting:
        await event.respond(welcome_msg_text)
    else:
        await event.delete()

@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def handle_owner_reply(event):
    user_id = str(event.chat_id)
    if user_id not in waiting_list:
        waiting_list.add(user_id)
        save_memory(waiting_list)

async def main():
    await client.start()
    print("UserBot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
