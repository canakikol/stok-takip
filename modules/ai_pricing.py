import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils import load_data, load_sales, load_customers, save_data, get_today

def calculate_demand_factor(product_id, days=30):
    """Ürünün son 30 günlük satış hızını hesapla"""
    sales_df = load_sales()
    products_df = load_data()
    
    if sales_df.empty:
        return 1.0  # Satış verisi yoksa nötr faktör
    
    # Son 30 günlük satışları filtrele
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    product_sales = sales_df[
        (sales_df['urun_id'] == product_id) & 
        (pd.to_datetime(sales_df['tarih']).dt.date >= start_date) &
        (pd.to_datetime(sales_df['tarih']).dt.date <= end_date)
    ]
    
    if product_sales.empty:
        return 1.0  # Satış yoksa nötr faktör (0.5 yerine 1.0)
    
    total_sales = product_sales['adet'].sum()
    avg_daily_sales = total_sales / days
    
    # Talep faktörü hesaplama (0.8 - 1.5 arası - daha dengeli)
    if avg_daily_sales == 0:
        return 1.0  # Satış yoksa nötr faktör
    elif avg_daily_sales <= 1:
        return 0.9  # Düşük talep - hafif düşüş
    elif avg_daily_sales <= 3:
        return 1.0  # Normal talep - nötr
    elif avg_daily_sales <= 5:
        return 1.2  # Yüksek talep - artış
    else:
        return 1.4  # Çok yüksek talep - büyük artış

def calculate_stock_factor(current_stock, minimum_stock):
    """Stok seviyesine göre fiyat faktörü hesapla"""
    if current_stock <= minimum_stock * 0.5:
        return 1.2  # Çok düşük stok - fiyat artışı
    elif current_stock <= minimum_stock:
        return 1.1  # Düşük stok - hafif artış
    elif current_stock <= minimum_stock * 2:
        return 1.0  # Normal stok - nötr
    elif current_stock <= minimum_stock * 5:
        return 0.95  # Yüksek stok - çok hafif indirim
    else:
        return 0.9  # Çok yüksek stok - hafif indirim

def calculate_seasonal_factor():
    """Mevsimsel faktör hesapla (tekstil için)"""
    current_month = datetime.now().month
    
    # Tekstil sektörü mevsimsellik faktörleri (daha dengeli)
    seasonal_factors = {
        1: 0.95,  # Ocak - Kış sezonu sonu
        2: 0.9,   # Şubat - Sezon sonu indirimleri
        3: 1.05,  # Mart - İlkbahar başlangıcı
        4: 1.1,   # Nisan - İlkbahar sezonu
        5: 1.05,  # Mayıs - İlkbahar devam
        6: 1.0,   # Haziran - Yaz başlangıcı
        7: 1.1,   # Temmuz - Yaz sezonu
        8: 1.05,  # Ağustos - Yaz devam
        9: 1.15,  # Eylül - Sonbahar başlangıcı
        10: 1.1,  # Ekim - Sonbahar sezonu
        11: 1.05, # Kasım - Kış başlangıcı
        12: 1.0   # Aralık - Kış sezonu
    }
    
    return seasonal_factors.get(current_month, 1.0)

def calculate_customer_segment_factor(customer_segment):
    """Müşteri segmentine göre fiyat faktörü"""
    segment_factors = {
        'Premium': 1.1,      # %10 yüksek fiyat
        'Orta': 1.0,         # Normal fiyat
        'Ekonomik': 0.95,    # %5 indirim
        'Yeni': 0.97         # %3 indirim
    }
    
    return segment_factors.get(customer_segment, 1.0)

def calculate_ai_price(product_id, base_price, customer_segment='Orta'):
    """AI destekli fiyat hesaplama"""
    
    # Temel faktörler
    demand_factor = calculate_demand_factor(product_id)
    seasonal_factor = calculate_seasonal_factor()
    customer_factor = calculate_customer_segment_factor(customer_segment)
    
    # Ürün bilgilerini al
    products_df = load_data()
    product = products_df[products_df['id'] == product_id]
    
    if product.empty:
        return base_price
    
    current_stock = product.iloc[0]['stok']
    minimum_stock = product.iloc[0]['minimum_stok']
    
    # Stok faktörü
    stock_factor = calculate_stock_factor(current_stock, minimum_stock)
    
    # AI fiyat hesaplama
    ai_price = base_price * demand_factor * stock_factor * seasonal_factor * customer_factor
    
    # Kar marjı kontrolü (minimum %20, maksimum %50)
    cost_price = product.iloc[0]['alis_fiyati']
    min_price = cost_price * 1.2  # %20 kar marjı
    max_price = cost_price * 1.5  # %50 kar marjı
    
    # Minimum fiyat koruması - mevcut fiyatın %90'ından düşük olamaz
    min_price_protection = base_price * 0.9
    min_price = max(min_price, min_price_protection)
    
    ai_price = max(min_price, min(ai_price, max_price))
    
    return round(ai_price, 2)

def get_pricing_recommendations():
    """Tüm ürünler için fiyat önerileri oluştur"""
    products_df = load_data()
    recommendations = []
    
    for _, product in products_df.iterrows():
        current_price = product['satis_fiyati']
        ai_price = calculate_ai_price(product['id'], current_price)
        
        price_change = ai_price - current_price
        price_change_percent = (price_change / current_price * 100) if current_price > 0 else 0
        
        recommendation = {
            'id': product['id'],
            'urun_adi': product['isim'],
            'kategori': product['kategori'],
            'mevcut_fiyat': current_price,
            'onerilen_fiyat': ai_price,
            'fiyat_degisimi': price_change,
            'fiyat_degisimi_yuzde': price_change_percent,
            'stok': product['stok'],
            'minimum_stok': product['minimum_stok'],
            'alis_fiyati': product['alis_fiyati'],
            'kar_marji_mevcut': ((current_price - product['alis_fiyati']) / product['alis_fiyati'] * 100) if product['alis_fiyati'] > 0 else 0,
            'kar_marji_onerilen': ((ai_price - product['alis_fiyati']) / product['alis_fiyati'] * 100) if product['alis_fiyati'] > 0 else 0
        }
        
        recommendations.append(recommendation)
    
    return pd.DataFrame(recommendations)

def show_ai_pricing():
    st.header("🤖 Stockly AI Fiyatlandırma")
    st.markdown("Yapay zeka destekli dinamik fiyatlandırma sistemi ile ürünlerinizin fiyatlarını optimize edin.")
    st.markdown("---")
    
    # Fiyat önerilerini al
    recommendations_df = get_pricing_recommendations()
    
    if not recommendations_df.empty:
        # Özet istatistikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_products = len(recommendations_df)
            st.metric("Toplam Ürün", total_products)
        
        with col2:
            price_increases = len(recommendations_df[recommendations_df['fiyat_degisimi'] > 0])
            st.metric("Fiyat Artışı Önerisi", price_increases)
        
        with col3:
            price_decreases = len(recommendations_df[recommendations_df['fiyat_degisimi'] < 0])
            st.metric("Fiyat Düşüşü Önerisi", price_decreases)
        
        with col4:
            avg_change = recommendations_df['fiyat_degisimi_yuzde'].mean()
            st.metric("Ortalama Değişim (%)", f"{avg_change:.1f}%")
        
        st.markdown("---")
        
        # Fiyat önerileri tablosu
        st.write("### 📊 Fiyat Önerileri")
        
        # Filtreleme seçenekleri
        col1, col2 = st.columns(2)
        
        with col1:
            filter_option = st.selectbox(
                "Filtreleme",
                ["Tümü", "Fiyat Artışı", "Fiyat Düşüşü", "Değişim Yok"]
            )
        
        with col2:
            sort_option = st.selectbox(
                "Sıralama",
                ["Fiyat Değişimi (%)", "Ürün Adı", "Kategori", "Stok Durumu"]
            )
        
        # Filtreleme uygula
        if filter_option == "Fiyat Artışı":
            filtered_df = recommendations_df[recommendations_df['fiyat_degisimi'] > 0]
        elif filter_option == "Fiyat Düşüşü":
            filtered_df = recommendations_df[recommendations_df['fiyat_degisimi'] < 0]
        elif filter_option == "Değişim Yok":
            filtered_df = recommendations_df[recommendations_df['fiyat_degisimi'] == 0]
        else:
            filtered_df = recommendations_df
        
        # Sıralama uygula
        if sort_option == "Fiyat Değişimi (%)":
            filtered_df = filtered_df.sort_values('fiyat_degisimi_yuzde', ascending=False)
        elif sort_option == "Ürün Adı":
            filtered_df = filtered_df.sort_values('urun_adi')
        elif sort_option == "Kategori":
            filtered_df = filtered_df.sort_values('kategori')
        elif sort_option == "Stok Durumu":
            filtered_df = filtered_df.sort_values('stok')
        
        # Tablo gösterimi
        if not filtered_df.empty:
            display_df = filtered_df[['urun_adi', 'kategori', 'mevcut_fiyat', 'onerilen_fiyat', 
                                   'fiyat_degisimi_yuzde', 'stok', 'kar_marji_mevcut', 'kar_marji_onerilen']].copy()
            display_df.columns = ['Ürün', 'Kategori', 'Mevcut Fiyat (₺)', 'Önerilen Fiyat (₺)', 
                                'Değişim (%)', 'Stok', 'Mevcut Kar (%)', 'Önerilen Kar (%)']
            
            # Fiyat değişimi renklendirmesi
            def color_price_change(val):
                if val > 0:
                    return 'background-color: #ffebee'  # Kırmızı (artış)
                elif val < 0:
                    return 'background-color: #e8f5e8'  # Yeşil (düşüş)
                else:
                    return ''
            
            st.dataframe(display_df.style.applymap(color_price_change, subset=['Değişim (%)']), 
                        use_container_width=True, height=400)
            
            # Toplu güncelleme seçenekleri
            st.markdown("---")
            st.write("### ✅ Toplu Fiyat Güncelleme")
            
            # Onay sistemi
            with st.expander("⚠️ Güncelleme Detayları"):
                st.write("**AI Fiyatlandırma Faktörleri:**")
                st.write("- **Talep Analizi:** Son 30 günlük satış hızı")
                st.write("- **Stok Kontrolü:** Düşük stok = fiyat artışı")
                st.write("- **Mevsimsellik:** Tekstil sektörü aylık faktörleri")
                st.write("- **Kar Marjı:** Minimum %20, maksimum %50")
                st.write("- **Fiyat Koruması:** Mevcut fiyatın %90'ından düşük olamaz")
                
                st.write("**Önerilen Strateji:**")
                st.write("1. Önce 'Sadece Artışları Uygula' ile test edin")
                st.write("2. Sonuçları kontrol edin")
                st.write("3. Gerekirse 'Tüm Önerileri Uygula' ile devam edin")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Tüm Önerileri Uygula", type="primary"):
                    # Onay sistemi
                    if st.session_state.get('confirm_all', False):
                        apply_all_recommendations(recommendations_df)
                    else:
                        st.session_state.confirm_all = True
                        st.warning("⚠️ **Dikkat:** Bu işlem tüm ürünlerin fiyatlarını değiştirecek!")
                        st.write(f"**Etkilenecek Ürün:** {len(recommendations_df)} adet")
                        st.write(f"**Ortalama Değişim:** %{avg_change:.1f}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Onayla ve Uygula", type="primary"):
                                apply_all_recommendations(recommendations_df)
                        with col_b:
                            if st.button("❌ İptal"):
                                st.session_state.confirm_all = False
                                st.rerun()
            
            with col2:
                if st.button("📈 Sadece Artışları Uygula", type="secondary"):
                    increases_df = recommendations_df[recommendations_df['fiyat_degisimi'] > 0]
                    if not increases_df.empty:
                        apply_recommendations(increases_df)
                    else:
                        st.info("Fiyat artışı önerisi bulunamadı.")
            
            with col3:
                if st.button("📉 Sadece Düşüşleri Uygula", type="secondary"):
                    decreases_df = recommendations_df[recommendations_df['fiyat_degisimi'] < 0]
                    if not decreases_df.empty:
                        apply_recommendations(decreases_df)
                    else:
                        st.info("Fiyat düşüşü önerisi bulunamadı.")
        else:
            st.info("Seçilen filtrelere uygun ürün bulunamadı.")
    else:
        st.info("Fiyat önerisi için ürün bulunamadı.")

def apply_recommendations(recommendations_df):
    """Seçilen önerileri uygula"""
    products_df = load_data()
    
    for _, rec in recommendations_df.iterrows():
        product_id = rec['id']
        new_price = rec['onerilen_fiyat']
        
        # Ürün fiyatını güncelle
        products_df.loc[products_df['id'] == product_id, 'satis_fiyati'] = new_price
    
    # Değişiklikleri kaydet
    save_data(products_df)
    st.success(f"✅ {len(recommendations_df)} ürünün fiyatı güncellendi!")
    st.rerun()

def apply_all_recommendations(recommendations_df):
    """Tüm önerileri uygula"""
    apply_recommendations(recommendations_df) 