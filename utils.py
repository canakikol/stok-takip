import pandas as pd
import os
import datetime
import random

DATA_PATH = "data/data.csv"
SALES_PATH = "data/sales.csv"
CUSTOMERS_PATH = "data/customers.csv"
SUPPLIERS_PATH = "data/suppliers.csv"
ORDERS_PATH = "data/orders.csv"

def load_data():
    """Ürün verilerini yükle"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["id", "isim", "kategori", "stok", "alis_fiyati", "satis_fiyati", "minimum_stok"])
        df.to_csv(DATA_PATH, index=False)
    else:
        df = pd.read_csv(DATA_PATH)
        # Kategori sütunu yoksa ekle
        if 'kategori' not in df.columns:
            df['kategori'] = 'Tekstil'
            df.to_csv(DATA_PATH, index=False)
        else:
            # Mevcut ürünlerin kategorilerini Tekstil olarak güncelle
            df['kategori'] = 'Tekstil'
            df.to_csv(DATA_PATH, index=False)
        # Minimum stok sütunu yoksa ekle
        if 'minimum_stok' not in df.columns:
            df['minimum_stok'] = 5
            df.to_csv(DATA_PATH, index=False)
    return df

def save_data(df):
    """Ürün verilerini kaydet"""
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

def load_sales():
    """Satış verilerini yükle"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(SALES_PATH):
        sales_df = pd.DataFrame(columns=["id", "urun_id", "tarih", "adet", "fiyat"])
        sales_df.to_csv(SALES_PATH, index=False)
    return pd.read_csv(SALES_PATH)

def save_sales(sales_df):
    """Satış verilerini kaydet"""
    os.makedirs("data", exist_ok=True)
    sales_df.to_csv(SALES_PATH, index=False)

def load_customers():
    """Müşteri verilerini yükle"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CUSTOMERS_PATH):
        customers_df = pd.DataFrame(columns=["id", "musteri_adi", "yas", "cinsiyet", "bolge", "son_satin_alma_tarihi", "toplam_satin_alma_sayisi", "toplam_harcama"])
        customers_df.to_csv(CUSTOMERS_PATH, index=False)
    return pd.read_csv(CUSTOMERS_PATH)

def save_customers(customers_df):
    """Müşteri verilerini kaydet"""
    os.makedirs("data", exist_ok=True)
    customers_df.to_csv(CUSTOMERS_PATH, index=False)

def load_suppliers():
    """Tedarikçi verilerini yükle"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(SUPPLIERS_PATH):
        suppliers_df = pd.DataFrame(columns=["id", "tedarikci_adi", "telefon", "email", "adres", "urun_kategorileri", "teslimat_suresi", "performans_puani", "son_siparis_tarihi", "aktif_durum"])
        suppliers_df.to_csv(SUPPLIERS_PATH, index=False)
    return pd.read_csv(SUPPLIERS_PATH)

def save_suppliers(suppliers_df):
    """Tedarikçi verilerini kaydet"""
    os.makedirs("data", exist_ok=True)
    suppliers_df.to_csv(SUPPLIERS_PATH, index=False)

def load_orders():
    """Sipariş verilerini yükle"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(ORDERS_PATH):
        orders_df = pd.DataFrame(columns=["id", "tedarikci_id", "urun_adi", "miktar", "birim_fiyat", "toplam_fiyat", "siparis_tarihi", "teslimat_tarihi", "durum", "notlar"])
        orders_df.to_csv(ORDERS_PATH, index=False)
    return pd.read_csv(ORDERS_PATH)

def save_orders(orders_df):
    """Sipariş verilerini kaydet"""
    os.makedirs("data", exist_ok=True)
    orders_df.to_csv(ORDERS_PATH, index=False)

def get_today():
    """Bugünün tarihini ISO formatında döndür"""
    return datetime.date.today().isoformat()

def check_low_stock(df):
    """Düşük stok uyarılarını kontrol et"""
    low_stock_items = df[df['stok'] <= df['minimum_stok']]
    return low_stock_items

def create_random_sales_history(num_days=90, min_adet=0, max_adet=3):
    """Her ürün için son num_days gün boyunca random satışlar oluşturur ve sales.csv'ye yazar."""
    df = load_data()
    sales = []
    today = datetime.date.today()
    sale_id = 1
    for _, urun in df.iterrows():
        for day in range(num_days):
            tarih = today - datetime.timedelta(days=(num_days - day - 1))
            adet = random.randint(min_adet, max_adet)
            if adet == 0:
                continue  # O gün satış yok
            fiyat = urun['satis_fiyati']
            sales.append({
                'id': sale_id,
                'urun_id': urun['id'],
                'tarih': tarih.isoformat(),
                'adet': adet,
                'fiyat': fiyat
            })
            sale_id += 1
    sales_df = pd.DataFrame(sales)
    sales_df.to_csv(SALES_PATH, index=False) 