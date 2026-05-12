// 1. Genel Mimari ve Erişim Bilgileri
const API_BASE_URL = "http://localhost:8000";

// Sayfa yüklendiğinde stokları getir
document.addEventListener('DOMContentLoaded', () => {
    fetchStocks();
});

// A. Stok Listesini Getirme (GET /admin/stocks)
async function fetchStocks() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/stocks`);
        if (!response.ok) throw new Error("Stok listesi alınamadı");

        const stocks = await response.json();
        renderStockTable(stocks);
        updateStats(stocks);
    } catch (error) {
        showFeedback("Hata: Veriler yüklenemedi!", "error");
    }
}

// Tabloyu yönergedeki "Satır İçi Güncelleme" mantığına göre oluşturur
function renderStockTable(stocks) {
    const tbody = document.getElementById('product-list');
    tbody.innerHTML = '';

    stocks.forEach(product => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${product.id}</td>
            <td>${product.name}</td>
            <td><span class="badge-size">${product.size}</span></td>
            <td>
                <div class="stock-update-group" style="display: flex; gap: 10px; align-items: center;">
                    <input type="number" id="input-${product.id}" value="${product.stock}" min="0" style="width: 60px; padding: 5px;">
                    <button onclick="updateStock(${product.id})" class="btn-primary" style="padding: 5px 10px; font-size: 12px;">Güncelle</button>
                </div>
            </td>
            <td>
                <button onclick="deleteProduct(${product.id})" style="background: none; border: none; cursor: pointer; font-size: 16px;">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// B. Yeni Ürün Ekleme (POST /admin/stocks/add)
document.getElementById('productForm').onsubmit = async (e) => {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');

    const payload = {
        name: document.getElementById('name').value,
        size: document.getElementById('size').value,
        stock: parseInt(document.getElementById('stock').value)
    };

    // Yükleme Durumu: Butonu pasif yap
    submitBtn.disabled = true;
    submitBtn.innerText = "Ekleniyor...";

    try {
        const response = await fetch(`${API_BASE_URL}/admin/stocks/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            showFeedback("Ürün başarıyla eklendi!", "success");
            closeModal();
            fetchStocks();
            e.target.reset();
        } else {
            showFeedback("Ekleme başarısız (422 Hatası).", "error");
        }
    } catch (error) {
        showFeedback("Bağlantı hatası!", "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Kaydet";
    }
};

// C. Stok Miktarı Güncelleme (POST /admin/stocks/update/{id})
async function updateStock(productId) {
    const inputField = document.getElementById(`input-${productId}`);
    const newCount = inputField.value;
    const btn = event.target;

    btn.disabled = true; // Yükleme Durumu

    try {
        const response = await fetch(`${API_BASE_URL}/admin/stocks/update/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_count: parseInt(newCount) })
        });

        const result = await response.json();

        if (response.ok) {
            // Bildirim gönderilen kişi sayısını göster
            showFeedback(`Stok güncellendi! ${result.notifications_sent} kişiye Telegram bildirimi gitti.`, "success");
            fetchStocks();
        } else {
            showFeedback("Hata: Ürün bulunamadı veya geçersiz veri (404/422).", "error");
        }
    } catch (error) {
        showFeedback("Sunucuya bağlanılamadı!", "error");
    } finally {
        btn.disabled = false;
    }
}

// D. Ürün Silme (DELETE /admin/stocks/delete/{id})
async function deleteProduct(productId) {
    if (!confirm("Bu ürünü silmek istediğinize emin misiniz?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/stocks/delete/${productId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showFeedback("Ürün silindi.", "success");
            fetchStocks();
        } else {
            showFeedback("Silme işlemi başarısız.", "error");
        }
    } catch (error) {
        showFeedback("Bağlantı hatası!", "error");
    }
}

// Yardımcı Fonksiyonlar
function updateStats(stocks) {
    document.getElementById('total-products').innerText = stocks.length;
    document.getElementById('low-stock').innerText = stocks.filter(s => s.stock === 0).length;
}

function showFeedback(message, type) {
    // Hata yönetimi için görsel geri bildirim
    alert(message);
}

function openModal() { document.getElementById('productModal').style.display = 'flex'; }
function closeModal() { document.getElementById('productModal').style.display = 'none'; }

// Sekme geçişleri için (Talepler sekmesi statik kalabilir veya API'ye bağlanabilir)
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    document.getElementById(tabName + '-sekmesi').style.display = 'block';
    document.getElementById('nav-' + tabName).classList.add('active');
}