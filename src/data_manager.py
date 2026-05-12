import json
import os

STOCKS_FILE = "data/stoklar.json"
DEMANDS_FILE = "data/talepler.json"

def load_json(file_path):
    """Dosyayı okur, yoksa boş liste döner."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(file_path, data):
    """Veriyi JSON dosyasına düzenli bir şekilde kaydeder."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- STOK İŞLEMLERİ ---

def get_all_stocks():
    return load_json(STOCKS_FILE)

def update_stock(product_id: int, new_count: int):
    """Stoğu günceller ve güncellenen ürünü döner."""
    stocks = load_json(STOCKS_FILE)
    for product in stocks:
        if product["id"] == product_id:
            product["stock"] = new_count
            save_json(STOCKS_FILE, stocks)
            return product
    return None

# --- TALEP İŞLEMLERİ ---

def add_demand(chat_id: int, product_name: str, size: str):
    """Kullanıcı talebini listeye ekler."""
    demands = load_json(DEMANDS_FILE)
    new_demand = {
        "chat_id": chat_id,
        "product_name": product_name,
        "size": size,
        "status": "waiting" # Beklemede
    }
    demands.append(new_demand)
    save_json(DEMANDS_FILE, demands)
    return True

def check_stock_status(product_name: str, size: str):
    """Ürünün stokta olup olmadığını kontrol eder."""
    stocks = get_all_stocks()
    # size None gelirse boş stringe çevirelim ki .lower() çökmesin
    safe_size = str(size).lower() if size else "belirtilmedi"
    for s in stocks:
        s_name = s.get("name", "").lower()
        s_size = str(s.get("size", "")).lower()
        
        # İsim ve beden eşleşiyor mu bakıyoruz (Case insensitive - büyük/küçük harf duyarsız)
        if s_name == product_name.lower() and s_size == safe_size:
            return s["stock"]
    return -1 # Ürün hiç bulunamadıysa

def get_all_stock_names():
    """stok listesindeki tüm ürün isimlerini döndürür"""
    try:
        with open("data/stoklar.json", "r", encoding="utf-8") as f:
            stocks = json.load(f)
            # JSON yapın liste içindeki objelerse (örn: [{"name": "Ürün1", ...}])
            return [stock.get("name") for stock in stocks if stock.get("name")]
    except Exception as e:
        print(f"Veri okuma hatası: {e}")
        return []
