# 🤖 Stock Assistant AI
**KOBİ'ler İçin Akıllı Stok Takibi ve AI Bildirim Asistanı**

Bu proje, KOBİ'lerin stok yönetimini dijitalleştiren ve stokta olmayan ürünler geldiğinde bekleyen müşterilere **Gemini 3.1 Flash-lite** kullanarak kişiselleştirilmiş bildirimler gönderen uçtan uca bir çözümdür.

---

## 🚀 Öne Çıkan Özellikler

- **Akıllı Eşleştirme:** Kullanıcının doğal dil ile yazdığı talepleri *(Örn: "Nayk 42 numara siyah gelsin")* stok listesiyle semantik olarak eşleştirir.
- **AI Bildirim Motoru:** Stok güncellendiğinde, bekleyen kullanıcılara her seferinde farklı, samimi ve heyecan verici mesajlar oluşturur.
- **KOBİ Yönetim Paneli:** Stok ekleme, silme ve güncelleme işlemlerinin yapılabildiği modern bir dashboard.
- **Talep Takip Sistemi:** Hangi ürüne ne kadar talep olduğunu analiz ederek KOBİ'ye stok planlama verisi sunar.

---

## 🛠️ Teknik Mimari

| Katman | Teknoloji |
|---|---|
| **Backend** | FastAPI (Python 3.10+) |
| **Yapay Zeka** | Google Gemini 3.1 Flash-lite (LLM) |
| **Bot Platformu** | Telegram Bot API |
| **Veri Yönetimi** | JSON *(Hackathon kapsamında hızlı ve taşınabilir veri yönetimi için tercih edilmiştir.)* |

---

## 💻 Kurulum ve Çalıştırma

> **Not:** Projenin Python 3.10 veya üzeri sürümlerde çalıştırılması tavsiye edilir.

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/utkuakkusoglu/yzta-hackathon-ai-stock-assistant.git
cd yzta-hackathon-ai-stock-assistant
```

### 2. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 3. Yapılandırma (Environment Variables)

Projenin çalışması için gerekli olan **Gemini API Key**, **Telegram Bot Token** ve **Bot Username** bilgileri, güvenlik protokolleri gereği repo içerisinde paylaşılmamıştır.

> Değerlendirme kolaylığı açısından bu anahtarlar **Pitch Deck (Sunum Dosyası)** içerisinde paylaşılmıştır.

1. Ana dizinde .env dosyası oluşturun.
2. Slaytta verilen GEMINI_API_KEY ve TELEGRAM_BOT_TOKEN bilgilerini .env dosyasına yapıştırın.

### 4. Sistemi Başlatın

#### A. Backend & Bot Servisi

Projenin beyni olan FastAPI ve Telegram Botu'nu başlatmak için terminale şu komutu yazın:

**Windows:**
```bash
python main.py
```

**macOS / Linux / WSL:**
```bash
python3 main.py
```

Backend çalıştıktan sonra API dokümantasyonuna [`http://localhost:8000/docs`](http://localhost:8000/docs) adresinden erişebilirsiniz.

#### B. KOBİ Yönetim Paneli (Frontend)

Yeni bir terminal sekmesi açıp `AdminPanel` klasörü içinde bir Python sunucusu başlatın:

**macOS / Linux / WSL:**
```bash
cd AdminPanel
python3 -m http.server 5500
```

**Windows:**
```bash
cd AdminPanel
python -m http.server 5500
```

Panel yayına girdikten sonra tarayıcınızdan [`http://localhost:5500`](http://localhost:5500) adresine giderek sistemi kullanmaya başlayabilirsiniz.

---

## 🏗️ Proje Yapısı

```
.
├── main.py               # Uygulama giriş noktası
├── config.py            # Yapılandırma ve Environment (.env) yönetimi
├── schemas.py           # Pydantic veri modelleri ve doğrulama (Validation)
├── requirements.txt      # Python bağımlılıkları
├── src/                  # Backend mantığı, API router'ları ve AI entegrasyon servisleri
├── AdminPanel/           # KOBİ'lerin stok yönettiği frontend arayüzü (HTML/JS/CSS)
└── data/                 # Stok listesi ve kullanıcı taleplerinin tutulduğu yerel veritabanı dosyaları
```

---

## 👥 Ekip

**Utku Akkuşoğlu** & **Betül Sirkeci**
