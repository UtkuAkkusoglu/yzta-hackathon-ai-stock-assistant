import uvicorn
import threading
from fastapi import FastAPI, HTTPException
from src.bot_service import run_bot, send_stock_alert
from fastapi.middleware.cors import CORSMiddleware
from src import data_manager
from src.routers import admin

app = FastAPI(title="Stock Assistant", description="KOBİ'ler için stok yönetimi ve bildirim sistemi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Hackathon için her yere izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)

def start_bot():
    # Botun sonsuz döngüsünü ayrı bir işçiye (thread) veriyoruz
    run_bot()

@app.on_event("startup")
async def on_startup():
    # Sistem açılırken botu arka planda başlat
    threading.Thread(target=start_bot, daemon=True).start()

@app.get("/")
async def root():
    return {"message": "Stock Assistant API Çalışıyor!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


