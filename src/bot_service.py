import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()

# .env'den token'ı çekiyoruz
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu verildiğinde çalışan fonksiyon"""
    await update.message.reply_text(
        f"Selam! Ben Stok Asistanı. 👋\n"
        f"Takip etmemi istediğin ürünü yazabilirsin.\n"
        f"Chat ID numaran: {update.effective_chat.id}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıdan herhangi bir metin geldiğinde çalışan fonksiyon"""
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    print(f"Yeni Mesaj Geldi ({chat_id}): {user_text}")
    
    # Burası ileride Gemini fonksiyonuyla bağlanacak
    await update.message.reply_text(f"'{user_text}' talebini aldım, stokları senin için takip edeceğim!")

def run_bot():
    """Botu başlatan ana fonksiyon"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutları ve mesaj dinleyicileri ekliyoruz
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram Bot dinlemede...")
    app.run_polling()