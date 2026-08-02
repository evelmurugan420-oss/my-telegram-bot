        await context.bot.send_message(chat_id=partner_id, text="⚠️ உங்க பார்ட்னர் சாட்டை விட்டு வெளியேறிட்டாங்க. புது பார்ட்னரைத் தேட '/find' அனுப்புங்க.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("தேடல் நிறுத்தப்பட்டது.")
    else:
        await update.message.reply_text("நீங்க எந்த சாட்டிலும் இல்லை.")

def main():
    # Render போர்ட் சர்வர் பிக்ஸ் (Fix for Render Port Timeout Error)
    def run_dummy_server():
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        server.serve_forever()

    Thread(target=run_dummy_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find_partner))
    app.add_handler(CommandHandler("exit", exit_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Bot is running successfully on Cloud...")
    app.run_polling()

if __name__ == '__main__':
    main()
