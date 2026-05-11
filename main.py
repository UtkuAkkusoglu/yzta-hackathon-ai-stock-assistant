import uvicorn
import threading
from fastapi import FastAPI, HTTPException
from src.bot_service import run_bot, send_stock_alert
from src import data_manager


app = FastAPI(title="Stock Assistant")

# --- ENDPOINT'LER ---

@app.get("/")
async def root():
    return {"message": "Stock Assistant API Çalışıyor!"}

@app.get("/stoklar")
async def get_stoklar():
    """Tüm stok listesini getirir"""
    return data_manager.get_all_stocks()

@app.post("/stok-guncelle")
async def stok_guncelle(product_id: int, new_count: int):
    # 1. Önce listeyi boş olarak tanımlayalım (Varsayılan değer)
    waiting_users = []

    # 2. stokları güncelle
    updated_product = data_manager.update_stock(product_id, new_count)
    
    if not updated_product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # 3. Eğer yeni stok 0'dan büyükse, bekleyen var mı diye bak
    if new_count > 0:
        p_name = updated_product["name"]
        p_size = updated_product["size"]
        
        # Talepler listesini oku
        all_demands = data_manager.load_json(data_manager.DEMANDS_FILE)
        
        # Bu ürünü ve bedeni bekleyenleri filtrele
        waiting_users = [
            d for d in all_demands 
            if d["product_name"].lower() == p_name.lower() 
            and d["size"].lower() == p_size.lower() 
            and d["status"] == "waiting"
        ]

        # 3. Bekleyen her kullanıcıya bildirim at ve talebi temizle (veya status güncelle)
        for demand in waiting_users:
            # Bildirimi fırlat!
            await send_stock_alert(demand["chat_id"], p_name, p_size)
            # Talebi "tamamlandı" olarak işaretle ki bir daha bildirim gitmesin
            demand["status"] = "completed"

        # Güncellenmiş talepleri kaydet
        data_manager.save_json(data_manager.DEMANDS_FILE, all_demands)

    return {"status": "success", "updated_product": updated_product, "notifications_sent": len(waiting_users)}

def start_bot():
    # Botun sonsuz döngüsünü ayrı bir işçiye (thread) veriyoruz
    run_bot()

@app.on_event("startup")
async def on_startup():
    # Sistem açılırken botu arka planda başlat
    threading.Thread(target=start_bot, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


