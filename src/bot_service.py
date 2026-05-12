import os
import asyncio
from src.config import settings
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Kendi yazdığımız modülleri içe aktarıyoruz
from src.data_manager import add_demand, check_stock_status, get_all_stock_names, is_duplicate_demand
from src.ai_service import ai_engine  # AI Servisimiz

TOKEN = settings.TELEGRAM_BOT_TOKEN

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

    # 1. ADIM: AI ile Akıllı Analiz ve Eşleştirme (Entity Extraction + Semantic Matching)
    # Mevcut stok isimlerini alıyoruz ki Gemini neyi eşleştireceğini bilsin
    all_stocks = get_all_stock_names()
    
    # Gemini hem metni okuyor hem de stok listesindeki en yakın ürünü seçiyor
    # "Nayk 42" -> {"matched_product": "Siyah Nike Air Max", "size": "42"}
    ai_results = ai_engine.analyze_and_match(user_text, all_stocks)
    
    final_product_name = ai_results.get("matched_product")
    p_size = ai_results.get("size")

    if not p_size or str(p_size).lower() in ["none", "null", "undefined", ""]:
        p_size = "belirtilmedi"

    # Eğer AI listeden hiçbir şeyle eşleştiremezse (matched_product null dönerse)
    if not final_product_name:
        await update.message.reply_text(
            "Üzgünüm, hangi ürünü istediğini tam anlayamadım veya stok listemizde benzer bir ürün bulamadım. "
            "Biraz daha detay verir misin? 🤔"
        )
        return

    # 2. ADIM: STOK KONTROLÜ
    # AI'dan gelen "temizlenmiş" ürün adı ve beden ile kontrol yapıyoruz
    current_stock = check_stock_status(final_product_name, p_size)

    if current_stock > 0:
        # Ürün stokta varsa kullanıcıya müjdeyi ver
        await update.message.reply_text(
            f"✅ Müjde! Aradığın '{final_product_name}' ({p_size if p_size else 'Standart'}) stokta var!\n"
            f"Şu an {current_stock} adet mevcut. Hemen alabilirsin! 🚀"
        )
    else:
        if is_duplicate_demand(chat_id, final_product_name, p_size):
            await update.message.reply_text(
                f"Zaten '{final_product_name}' ({p_size}) için bir talebiniz var. 🫡\n"
                "Stok geldiğinde size haber vereceğimizden emin olabilirsiniz, nöbetteyiz! ✨"
            )
        else:
            # Yeni talep ekle
            add_demand(chat_id, final_product_name, p_size)
            await update.message.reply_text(
                f"🔍 '{final_product_name}' ({p_size}) şu an stokta yok.\n"
                "Talebinizi aldım! Stok geldiği an ilk size haber vereceğim. 🫡"
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
    app.run_polling(close_loop=False, stop_signals=False)

