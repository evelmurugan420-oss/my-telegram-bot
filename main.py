import logging
import os
import asyncio
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8905299984:AAE6dC5_caVZkXVMfJBjvUctNp8CO1nGvDg"
CHANNEL_USERNAME = "@detingchannel"

waiting_users = []
active_chats = {}

async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
        return False
    except TelegramError:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    subscribed = await is_user_subscribed(user_id, context)
    if not subscribed:
        # நேரடிச் சரியான லிங்க் இங்கே இணைக்கப்பட்டுள்ளது
        keyboard = [[InlineKeyboardButton("📢 Join Channel Here", url="https://t.me")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ நீங்க இன்னும் நம்ம சேனல்ல ஜாயின் பண்ணல!\n\nபாட்டைப் பயன்படுத்த முதலில் கீழே உள்ள பொத்தானை அழுத்தி நம்ம சேனல்ல ஜாயின் பண்ணிட்டு, அப்புறம் மறுபடி /start குடுங்க. 👍",
            reply_markup=reply_markup
        )
        return

    reply_keyboard = [['/find - Find Partner', '/exit - Exit Chat']]
    await update.message.reply_text(
        "👋 Welcome! Stranger கூட பேசத் தொடங்க கீழே உள்ள '/find' பொத்தானை அழுத்துங்க.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    subscribed = await is_user_subscribed(user_id, context)
    if not subscribed:
        await update.message.reply_text("⚠️ சாட் செய்ய முதலில் நம்ம சேனல்ல இணைந்து இருக்க வேண்டும்! /start கொடுத்துச் சரிபார்க்கவும்.")
        return

    if user_id in active_chats:
        await update.message.reply_text("நீங்க ஏற்கனவே ஒரு சாட்டில் தான் இருக்கீங்க! 😅")
        return
    if user_id in waiting_users:
        await update.message.reply_text("உங்களுக்கான பார்ட்னரைத் தேடிட்டு இருக்கேன்... கொஞ்சம் வெயிட் பண்ணுங்க! 🔍")
        return

    if not waiting_users:
        waiting_users.append(user_id)
        await update.message.reply_text("யாராவது ஆன்லைனில் வரும் வரை வெயிட் பண்ணுங்க... 🔍")
    else:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await context.bot.send_message(chat_id=user_id, text="🎯 Partner கிடைச்சிட்டாங்க! பேசத் தொடங்குங்க. வெளியேற '/exit' அனுப்புங்க.")
        await context.bot.send_message(chat_id=partner_id, text="🎯 Partner கிடைச்சிட்டாங்க! பேசத் தொடங்குங்க. வெளியேற '/exit' அனுப்புங்க.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        await update.message.reply_text("பேசத் தொடங்க முதலில் கீழே உள்ள '/find' பொத்தானை அழுத்துங்க.")

async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        del active_chats[user_id]
        del active_chats[partner_id]
        await context.bot.send_message(chat_id=user_id, text="❌ நீங்க சாட்டை விட்டு வெளியேறிட்டீங்க. புது பார்ட்னரைத் தேட '/find' அனுப்புங்க.")
        await context.bot.send_message(chat_id=partner_id, text="⚠️ உங்க பார்ட்னர் சாட்டை விட்டு வெளியேறிட்டாங்க. புது பார்ட்னரைத் தேட '/find' அனுப்புங்க.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("தேடல் நிறுத்தப்பட்டது.")
    else:
        await update.message.reply_text("நீங்க எந்த சாட்டிலும் இல்லை.")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

def main():
    Thread(target=run_dummy_server, daemon=True).start()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find_partner))
    app.add_handler(CommandHandler("exit", exit_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot is starting successfully on Cloud...")
    app.run_polling()

if __name__ == '__main__':
    main()
