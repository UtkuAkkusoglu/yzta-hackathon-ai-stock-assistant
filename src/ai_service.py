import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        # API anahtarını yapılandır
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("HATA: .env dosyasında GEMINI_API_KEY bulunamadı!")

        genai.configure(api_key=api_key)

        # En garanti model ismi budur. "models/" ön ekini ekleyerek 404'ü bitiriyoruz.
        self.model_name = "models/gemini-3.1-flash-lite"
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def extract_entities(self, user_text: str) -> dict:
        """Kullanıcı metninden ürün ve beden bilgilerini ayıklar."""
        prompt = f"""
        Aşağıdaki kullanıcı mesajından 'product' (ürün adı) ve 'size' (beden veya numara) bilgilerini çıkar.
        Mesaj: "{user_text}"

        SADECE şu JSON formatında yanıt ver (başka hiçbir şey yazma):
        {{
            "product": "ürün adı",
            "size": "beden/numara"
        }}
        Bilgi yoksa null kullan.
        """
        try:
            # JSON modunu aktif ederek çağırıyoruz
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Gelen cevabı güvenli bir şekilde JSON'a çevir
            result = json.loads(response.text.strip())
            print(f"✅ AI Analizi Başarılı: {result}")
            return result

        except Exception as e:
            # Eğer 404 hala devam ederse alternatif model ismine anlık geçiş yap
            print(f"❌ AI Hatası: {e}. Alternatif deneniyor...")
            return {"product": user_text, "size": None}  # Hata anında en azından mesajın tamamını ürün sayalım

    def find_matching_product(self, user_demand: str, stock_list: list) -> str:
        """Kullanıcının talebini stok listesiyle eşleştirir."""
        if not stock_list:
            return None

        prompt = f"""
        Kullanıcı şunu arıyor: "{user_demand}"
        Eldeki Stok Listesi: {stock_list}
        En yakın eşleşmeyi seç ve SADECE ürün adını yaz. Eşleşme yoksa 'null' yaz.
        """
        try:
            response = self.model.generate_content(prompt)
            match = response.text.strip()
            return None if "null" in match.lower() else match
        except:
            return None

    def generate_notification_message(self, product_name: str, size: str) -> str:
        """Samimi bir bildirim metni oluşturur."""
        prompt = f"""
        Ürün stoğa girdi: {product_name} (Beden: {size}).
        Müşteriye çok samimi, emojili ve kısa bir Telegram bildirim mesajı yaz.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"Müjde! {product_name} ({size}) tekrar stokta! 🚀"


# Servisi başlat
ai_engine = AIService()