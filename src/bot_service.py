import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Kendi yazdığımız modülleri içe aktarıyoruz
from src.data_manager import add_demand, check_stock_status, get_all_stock_names
from src.ai_service import ai_engine  # AI Servisimiz

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- KOMUTLAR (Start & Help) ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *StockMind AI Yardım Paneli*\n\n"
        "Şu komutları kullanabilirsin:\n"
        "/start - Botu başlatır\n"
        "/help - Yardım menüsü\n\n"
        "💡 *İpucu:* '42 numara mavi ayakkabı gelince haber ver' gibi doğal cümleler kurabilirsin."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Selam! Ben Stok Asistanı. 👋\n"
        f"Takip etmemi istediğin ürünü yazabilirsin.\n"
        f"Chat ID numaran: {update.effective_chat.id}"
      )


# --- ANA MESAJ İŞLEME MANTIĞI ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # 1. ADIM: AI ile metinden veri çıkarma (Entity Extraction)
    # Gemini mesajı okur: "Nike 42" -> {"product": "Nike", "size": "42"}
    ai_results = ai_engine.extract_entities(user_text)
    raw_product = ai_results.get("product")
    p_size = ai_results.get("size")

    if not raw_product:
        await update.message.reply_text(
            "Üzgünüm, hangi ürünü istediğini tam anlayamadım. Biraz daha detay verir misin? 🤔")
        return

    # 2. ADIM: AI ile Anlamsal Eşleştirme (Semantic Matching)
    # Kullanıcı "Nike" dedi ama stokta "Siyah Nike Air Max" var.
    # Mevcut stok isimlerini alıp Gemini'ye soruyoruz.
    all_stocks = get_all_stock_names()  # data_manager'da bu fonksiyonun olması gerekir
    matched_product = ai_engine.find_matching_product(raw_product, all_stocks)

    # Eğer anlamsal bir eşleşme bulamazsak kullanıcının yazdığını baz alıyoruz
    final_product_name = matched_product if matched_product else raw_product

    # 3. ADIM: STOK KONTROLÜ
    current_stock = check_stock_status(final_product_name, p_size)

    if current_stock > 0:
        await update.message.reply_text(
            f"✅ Müjde! Aradığın '{final_product_name}' ({p_size if p_size else 'Standart'}) stokta var!\n"
            f"Şu an {current_stock} adet mevcut. Hemen alabilirsin! 🚀"
        )
    else:
        # Ürün yok veya bitmişse talebi kaydet
        add_demand(chat_id, final_product_name, p_size)
        await update.message.reply_text(
            f"🔍 '{final_product_name}' ({p_size if p_size else 'Standart'}) şu an stokta yok.\n"
            "Ama merak etme, senin için nöbetteyim! Stok geldiği an haber vereceğim. 🫡"
        )


# --- BİLDİRİM GÖNDERİMİ ---
async def send_stock_alert(chat_id: int, product_name: str, size: str):
    bot = Bot(token=TOKEN)

    # AI ile dinamik ve samimi bir bildirim metni oluşturuyoruz
    # (ai_service.py içindeki fonksiyonu kullanıyoruz)
    alert_message = ai_engine.generate_notification_message(product_name, size)

    try:
        await bot.send_message(chat_id=chat_id, text=alert_message, parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"Bildirim Hatası: {e}")
        return False


def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Telegram Bot AI Destekli ve Güvenli Modda Çalışıyor...")
    # Sinyal ve Loop ayarlarını geri getirdik
    app.run_polling(close_loop=False, stop_signals=False)

