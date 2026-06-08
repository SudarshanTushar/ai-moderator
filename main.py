from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# --- CONFIGURATION (Isko config.py ya .env me shift karenge baad me) ---
API_ID = 1234567               # my.telegram.org se milega
API_HASH = "your_api_hash"     # my.telegram.org se milega
BOT_TOKEN = "your_bot_token"   # BotFather se milega
ADMIN_GROUP_ID = -10012345678  # Wo private group jahan approval aayenge

# 1. Initialize Bot (Admin ko report bhejne aur action lene ke liye)
bot = Client("admin_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 2. Initialize Userbot (Group me messages aur VC monitor karne ke liye)
userbot = Client("monitor_userbot", api_id=API_ID, api_hash=API_HASH)

# --- USERBOT: Chat Monitoring ---
@userbot.on_message(filters.group & filters.text)
async def monitor_chat(client, message):
    # Abhi ke liye ek simple word filter (Baad me yahan AI LLM/NLP connect karenge)
    bad_words = ["gali1", "gali2", "spamlink.com"] 
    
    text = message.text.lower()
    
    if any(word in text for word in bad_words):
        # Agar gaali ya spam mila, toh Bot ke through Admin Group me alert bhejo
        alert_text = (
            f"🚨 **Violation Detected!**\n"
            f"**User:** {message.from_user.mention} (`{message.from_user.id}`)\n"
            f"**Group:** {message.chat.title}\n"
            f"**Message:** {message.text}"
        )
        
        # Inline buttons (Approve/Ignore)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔨 Approve Ban", callback_data=f"ban_{message.from_user.id}_{message.chat.id}")],
            [InlineKeyboardButton("🔇 Mute 24h", callback_data=f"mute_{message.from_user.id}_{message.chat.id}")],
            [InlineKeyboardButton("❌ Ignore", callback_data="ignore")]
        ])
        
        await bot.send_message(chat_id=ADMIN_GROUP_ID, text=alert_text, reply_markup=buttons)

# --- BOT: Admin Approval Actions ---
@bot.on_callback_query()
async def admin_actions(client, callback_query):
    data = callback_query.data
    
    if data.startswith("ban"):
        _, user_id, chat_id = data.split("_")
        # Bot command bhejega ban karne ke liye
        await bot.ban_chat_member(int(chat_id), int(user_id))
        await callback_query.message.edit_text("✅ **User Banned Successfully by Admin.**")
        
    elif data == "ignore":
        await callback_query.message.edit_text("❌ **Action Ignored.**")

# --- START BOTH CLIENTS ---
async def main():
    await bot.start()
    await userbot.start()
    print("🚀 AI Moderator System Started!")
    from pyrogram import idle
    await idle()
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    bot.run(main())
