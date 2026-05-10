import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from src.data_manager import add_demand, check_stock_status

load_dotenv()

# .env'den token'ı çekiyoruz
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *StockMind AI Yardım Paneli*\n\n"
        "Şu komutları kullanabilirsin:\n"
        "/start - Botu başlatır ve selamlar\n"
        "/help - Bu yardım menüsünü gösterir\n\n"
        "💡 *İpucu:* Takip etmek istediğin ürünü 'Siyah Nike ayakkabı 42 numara gelince haber ver' gibi doğal bir dille yazabilirsin."
    )
    # parse_mode="Markdown" sayesinde yazıları kalın veya italik yapabilirsin
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu verildiğinde çalışan fonksiyon"""
    await update.message.reply_text(
        f"Selam! Ben Stok Asistanı. 👋\n"
        f"Takip etmemi istediğin ürünü yazabilirsin.\n"
        f"Chat ID numaran: {update.effective_chat.id}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # Şimdilik Gemini yokmuş gibi davranıyoruz
    # Kişi A, Gemini fonksiyonunu verince o fonksiyonu çağırıp user_text yerine 
    # oradan dönen 'ürün' ve 'beden' bilgilerini koyacağız.
    p_name = user_text 
    # p_size = "Belirtilmedi"
    p_size = "38"

    # 1. STOK KONTROLÜ
    current_stock = check_stock_status(p_name, p_size)

    if current_stock > 0:
        # Ürün zaten var!
        await update.message.reply_text(
            f"✅ Müjde! '{p_name}' şu an stoklarımızda {current_stock} adet mevcut.\n"
            "Beklemene gerek yok, hemen alabilirsin!"
        )
    elif current_stock == 0:
        # Ürün var ama bitmiş, listeye ekle
        add_demand(chat_id, p_name, p_size)
        await update.message.reply_text(
            f"🔍 '{p_name}' şu an tükenmiş görünüyor. Seni takip listesine aldım!\n"
            "Stok geldiği an sana buradan bildirim atacağım. 👋"
        )
    else:
        # Ürün katalogda hiç yok veya isim tam eşleşmedi
        await update.message.reply_text(
            "Hımm, bu ürünü kataloğumuzda tam bulamadım. 🧐\n"
            "İstersen ismini tam yazabilirsin (Örn: Siyah Nike Air Max)."
        )

async def send_stock_alert(chat_id: int, product_name: str, size: str):
    """Dışarıdan tetiklenebilen bildirim fonksiyonu"""
    bot = Bot(token=TOKEN)
    message = (
        f"🥳 **MÜJDE! BEKLEDİĞİN ÜRÜN GELDİ!**\n\n"
        f"📦 **Ürün:** {product_name}\n"
        f"📏 **Beden:** {size}\n\n"
        f"Stoklar yenilendi, bitmeden hemen almanı öneririm! 🏃‍♂️💨"
    )
    try:
        # Bot nesnesini kullanarak direkt mesaj atıyoruz
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        print(f"✅ {chat_id} numaralı kullanıcıya bildirim gönderildi.")
        return True
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi ({chat_id}): {e}")
        return False

def run_bot():
    """Botu başlatan ana fonksiyon"""
    # Yeni bir event loop oluşturuyoruz ve bu thread'e atıyoruz
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutları ve mesaj dinleyicileri ekliyoruz
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram Bot dinlemede...")
    app.run_polling(close_loop=False, stop_signals=False)