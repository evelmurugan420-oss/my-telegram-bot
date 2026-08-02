import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8905299984:AAE6dC5_caVZkXVMfJBjvUctNp8CO1nGvDg"

waiting_users = []
active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reply_keyboard = [['/find', '/exit']]
    
    await update.message.reply_text(
        "Welcome! Press /find to start chatting with a stranger.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_chats:
        await update.message.reply_text("You are already in a chat!")
        return
        
    if user_id in waiting_users:
        await update.message.reply_text("Searching for a partner... please wait.")
        return

    if not waiting_users:
        waiting_users.append(user_id)
        await update.message.reply_text("Waiting for someone to join... 🔍")
    else:
        partner_id = waiting_users.pop(0)
        
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        
        await context.bot.send_message(chat_id=user_id, text="🎯 Partner found! Start chatting. Type /exit to leave.")
        await context.bot.send_message(chat_id=partner_id, text="🎯 Partner found! Start chatting. Type /exit to leave.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        await update.message.reply_text("Type /find to search for a partner.")

async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        
        del active_chats[user_id]
        del active_chats[partner_id]
        
        await context.bot.send_message(chat_id=user_id, text="❌ You left the chat. Type /find to search again.")
        await context.bot.send_message(chat_id=partner_id, text="⚠️ Your partner left the chat. Type /find to search again.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("Search stopped.")
    else:
        await update.message.reply_text("You are not in an active chat.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find_partner))
    app.add_handler(CommandHandler("exit", exit_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
