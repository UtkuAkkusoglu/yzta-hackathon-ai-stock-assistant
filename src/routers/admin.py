from fastapi import APIRouter, HTTPException, Body
from typing import List
from src import data_manager, schemas
from src.bot_service import send_stock_alert

router = APIRouter(prefix="/admin", tags=["KOBİ Paneli"])

# 1. KOBİ'nin ürünleri göreceği liste
@router.get("/stocks", response_model=List[schemas.ProductResponse])
async def get_stocks():
    """Tüm stok listesini getirir"""
    return data_manager.get_all_stocks()

# 2. KOBİ'nin stok miktarını güncelleyeceği yer (Mesajı bu tetikliyor!)
@router.post("/stocks/update/{product_id}")
async def update_stock(product_id: int, update_data: schemas.ProductUpdate):
    """Mevcut bir ürünün stoğu arttığında bekleyenlere haber verir."""
    updated_product = data_manager.update_stock(product_id, update_data.new_count)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    count = 0
    if update_data.new_count > 0:
        count = await data_manager.notify_waiting_users(updated_product["name"], updated_product["size"], send_stock_alert)

    return {
        "status": "success", 
        "message": "Stok güncellendi", 
        "notifications_sent": count
    }

# 3. KOBİ'nin yeni ürün ekleyeceği yer
@router.post("/stocks/add", response_model=schemas.ProductResponse)
async def add_product(product: schemas.ProductCreate):
    """Yeni ürün stoğuyla beraber eklenirse bekleyenlere anında haber verir."""
    new_product = data_manager.add_new_product(product.name, product.size, product.stock)
    
    count = 0
    if product.stock > 0:
        # Ürün ilk kez eklendiğinde de bekleyen var mı diye bak
        count = await data_manager.notify_waiting_users(product.name, product.size, send_stock_alert)
        
    return new_product # schemas.ProductResponse sayesinde ID, name, size, stock döner

# 4. KOBİ'nin ürün sileceği yer
@router.delete("/stocks/delete/{product_id}")
async def delete_product(product_id: int):
    """Ürünü stok listesinden tamamen kaldırır"""
    success = data_manager.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ürün silinemedi veya bulunamadı")
    return {"status": "success", "message": f"ID: {product_id} olan ürün başarıyla silindi"}