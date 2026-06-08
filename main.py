# main.py
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config

# 1. Initialize Bot (Alerts bhejne aur ban/mute action lene ke liye)
bot = Client(
    "admin_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# 2. Initialize Userbot (Groups ko silent hoke monitor karne ke liye)
# Yahan hum in_memory=True aur session_string ka use kar rahe hain
userbot = Client(
    "monitor_userbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
    in_memory=True
)

# --- USERBOT: Chat Monitoring Logic ---
@userbot.on_message(filters.group & filters.text)
async def monitor_chat(client, message):
    # Abhi testing ke liye basic word filter (Baad me yahan AI model lagayenge)
    bad_words = ["abuse1", "spamlink", "scam"] 
    text = message.text.lower()
    
    # Agar message me koi bad word hai
    if any(word in text for word in bad_words):
        print(f"Violation detected by user: {message.from_user.first_name}")
        
        alert_text = (
            f"🚨 **Violation Detected!**\n\n"
            f"👤 **User:** {message.from_user.mention} (`{message.from_user.id}`)\n"
            f"👥 **Group:** {message.chat.title}\n"
            f"💬 **Message:** {message.text}"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔨 Approve Ban", callback_data=f"ban_{message.from_user.id}_{message.chat.id}")],
            [InlineKeyboardButton("🔇 Mute 24h", callback_data=f"mute_{message.from_user.id}_{message.chat.id}")],
            [InlineKeyboardButton("❌ Ignore", callback_data="ignore")]
        ])
        
        # Bot admin group me message bhejega
        try:
            await bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=alert_text, reply_markup=buttons)
        except Exception as e:
            print(f"Error sending message to admin group: {e}")

# --- BOT: Admin Approval Actions ---
@bot.on_callback_query()
async def admin_actions(client, callback_query):
    data = callback_query.data
    
    if data.startswith("ban"):
        _, user_id, chat_id = data.split("_")
        # User ko ban karna
        await bot.ban_chat_member(int(chat_id), int(user_id))
        await callback_query.message.edit_text(f"✅ **User Banned Successfully.**\n\n{callback_query.message.text}")
        
    elif data.startswith("mute"):
        # Mute logic hum aage add karenge, abhi ke liye sirf message edit karte hain
        await callback_query.message.edit_text(f"🔇 **User Muted for 24 hours.**\n\n{callback_query.message.text}")
        
    elif data == "ignore":
        await callback_query.message.edit_text(f"❌ **Action Ignored.**\n\n{callback_query.message.text}")

# --- MAIN RUN FUNCTION ---
async def main():
    print("Starting Bot and Userbot...")
    await bot.start()
    await userbot.start()
    print("🚀 AI Moderator System is Online!")
    
    from pyrogram import idle
    await idle()
    
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    bot.run(main())
