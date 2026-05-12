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

    # Aynı kullanıcı, aynı ürün ve beden için zaten beklemede mi?
    is_duplicate = any(
        d["chat_id"] == chat_id and 
        d["product_name"].lower() == product_name.lower() and 
        str(d.get("size", "")).lower() == str(size).lower() and
        d["status"] == "waiting"
        for d in demands
    )

    if is_duplicate:
        print(f"⚠️ {chat_id} için zaten aktif bir '{product_name}' talebi var. Tekrar eklenmedi.")
        return False

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
    """Ürünün stokta olup olmadığını kontrol eder (Normalize edilmiş bedenle)."""
    stocks = get_all_stocks()
    target_name = product_name.lower()
    target_size = normalize_size(size)

    for s in stocks:
        s_name = s.get("name", "").lower()
        s_size = normalize_size(s.get("size", ""))
        
        if s_name == target_name and s_size == target_size:
            return s.get("stock", 0)
            
    return -1 # Ürün katalogda hiç yoksa

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

def add_new_product(name: str, size: str, stock: int):
    """Yeni bir ürünü ID atayarak stok listesine ekler."""
    stocks = load_json(STOCKS_FILE)

    new_id = max([s["id"] for s in stocks], default=0) + 1
    safe_size = size if size and size.strip() != "" else "belirtilmedi"

    new_product = {"id": new_id, "name": name, "size": safe_size, "stock": stock}

    stocks.append(new_product)
    save_json(STOCKS_FILE, stocks)
    return new_product

def delete_product(product_id: int):
    """Ürünü listeden tamamen kaldırır."""
    stocks = load_json(STOCKS_FILE)
    stocks = [s for s in stocks if s["id"] != product_id]
    save_json(STOCKS_FILE, stocks)
    return True

def normalize_size(size_str: str) -> str:
    """Bedenleri her iki taraf için de standart bir formata getirir."""
    if not size_str or str(size_str).lower() == "none": 
        return "belirtilmedi"
    
    s = str(size_str).lower().strip()
    # Harita: Kullanıcı ne derse desin, sistemin anlayacağı ortak dil
    mapping = {
        "large": "l", "medium": "m", "small": "s", 
        "extra large": "xl", "x-large": "xl"
    }
    return mapping.get(s, s)

async def notify_waiting_users(p_name: str, p_size: str, send_alert_func):
    """
    Bekleyen kullanıcılara bildirim gönderir ve taleplerini günceller.
    Bu fonksiyon hem 'güncelleme' hem de 'yeni ekleme' anında tetiklenir.
    "yeni ekleme" anında tetiklenmesinin nedeni önceden istenen ve istendikten sonra silinen ürün, tekrar eklenirse kullanıcıların haberdar olması içindir.
    """
    safe_p_size = str(p_size).lower() if p_size else "belirtilmedi"
    all_demands = load_json(DEMANDS_FILE)
    
    waiting_users = [
        d for d in all_demands 
        if d["product_name"].lower() == p_name.lower() 
        and normalize_size(d.get("size", "")) == safe_p_size 
        and d["status"] == "waiting"
    ]

    for demand in waiting_users:
        await send_alert_func(demand["chat_id"], p_name, p_size)
        demand["status"] = "completed"

    if waiting_users:
        save_json(DEMANDS_FILE, all_demands)
    
    return len(waiting_users)

def is_duplicate_demand(chat_id: int, product_name: str, size: str) -> bool:
    """Kullanıcının hali hazırda bekleyen aynı talebi var mı kontrol eder."""
    demands = load_json(DEMANDS_FILE)
    target_name = product_name.lower()
    target_size = normalize_size(size)

    for d in demands:
        if (d["chat_id"] == chat_id and 
            d["product_name"].lower() == target_name and 
            normalize_size(d.get("size", "")) == target_size and 
            d["status"] == "waiting"):
            return True
    return False
