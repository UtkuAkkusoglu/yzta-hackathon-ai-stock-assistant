import os
import json
import google.generativeai as genai
from src.config import settings

class AIService:
    def __init__(self):
        # API anahtarını yapılandır
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("HATA: .env dosyasında GEMINI_API_KEY bulunamadı!")

        genai.configure(api_key=api_key)

        self.model_name = "models/gemini-3.1-flash-lite"
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def analyze_and_match(self, user_text: str, stock_list: list) -> dict:
        """
        Kullanıcı metnini analiz eder ve mevcut stok listesiyle eşleştirir.
        Tek seferde hem entity extraction hem de semantic matching yapar.
        """
        # GÜVENLİ BEDEN ÇIKARMA: item eğer sözlükse 'size' al, değilse boş bırak
        valid_sizes = []
        if stock_list and isinstance(stock_list[0], dict):
            valid_sizes = list(set([str(item.get('size', '')) for item in stock_list if 'size' in item]))

        prompt = f"""
        Sen bir stok asistanısın. Kullanıcının mesajından ürünü ve bedeni bulup mevcut stok listesiyle eşleştirmen gerekiyor.

        MEVCUT STOK LİSTESİ (Ürün İsimleri):
        {stock_list}

        GEÇERLİ BEDEN FORMATLARI:
        {valid_sizes}

        KULLANICI MESAJI: "{user_text}"

        GÖREVİN VE ÖNCELİKLERİN:
        1. ÜRÜN EŞLEŞTİRME: Mesajdaki ürünü stok listesindeki tam ismiyle eşleştir.
        
        2. BEDEN EŞLEŞTİRME (ÇOK KRİTİK): 
           - ÖNCE mesajda geçen beden bilgisini (Örn: large, m, 42) tespit et.
           - Bu bilgiyi {valid_sizes} listesindeki en uygun karşılığa dönüştür (Örn: "large" -> "L").
           - EĞER mesajda açıkça bir beden/numara geçiyorsa ASLA "belirtilmedi" yazma.
           - SADECE VE SADECE mesajda bedene dair hiçbir iz yoksa "belirtilmedi" yaz.

        SADECE şu JSON formatında yanıt ver:
        {{
            "matched_product": "stoktaki_tam_isim_veya_null",
            "size": "beden_veya_null"
        }}
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            result = json.loads(response.text.strip())
            print(f"✅ Akıllı Eşleşme Başarılı: {result}")
            return result
        except Exception as e:
            print(f"❌ AI Eşleşme Hatası: {e}")
            return {"matched_product": None, "size": None}

    def generate_notification_message(self, product_name: str, size: str) -> str:
        """Samimi ve heyecan verici bir bildirim metni oluşturur."""
        prompt = f"""
        GÖREV: Aşağıdaki ürünün stoğa girdiğini bekleyen müşteriye bildir.
        ÜRÜN: {product_name} 
        BEDEN: {size}

        KURALLAR:
        1. Mesaja doğrudan başla (Örn: "Selamlar!", "Harika bir haberim var!").
        2. "İşte mesajınız", "Müşteriye şunu de" gibi giriş cümleleri ASLA kullanma.
        3. Link verme, "Link aşağıda" gibi ifadeler kullanma.
        4. Samimi, heyecanlı ve emojili olsun.
        5. Müşteriye beklediği için teşekkür et.
        6. SADECE müşteriye gidecek mesaj metnini yaz.
        """
        try:
            response = self.model.generate_content(prompt)
            # Gemini bazen yine de tırnak içinde verebilir, onları temizleyelim
            message = response.text.strip().replace('"', '')
            return response.text.strip()
        except:
            return f"Müjde! Beklediğin {product_name} ({size}) sonunda geldi! 🚀 Hemen tükenmeden alabilirsin."

# Servisi başlat
ai_engine = AIService()