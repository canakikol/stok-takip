import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, load_sales
from modules.ai_pricing import show_ai_pricing

def show_ai_predictions():
    """AI tahmin sayfasını göster"""
    st.header("🤖 Stockly AI Modülleri")
    st.markdown("Yapay zeka destekli tahmin, fiyatlandırma ve analiz özellikleri.")
    st.markdown("---")
    
    # Tab menüsü
    tab1, tab2 = st.tabs(["📈 Stok Tahmini", "💰 AI Fiyatlandırma"])
    
    with tab1:
        show_stock_prediction_tab()
    
    with tab2:
        show_ai_pricing()

def show_stock_prediction_tab():
    """Stok tahmini sekmesi"""
    st.write("### 📈 Stok Tükenme Tahmini")
    st.markdown("Mevcut satış verilerine göre ürünlerin ne zaman tükeneceğini tahmin eder.")
    
    df = load_data()
    sales_df = load_sales()
    
    if df.empty or sales_df.empty:
        st.info("Tahmin için ürün ve satış verisi gerekli.")
        return
    
    # Her ürün için basit tahmin
    predictions = []
    for _, urun in df.iterrows():
        urun_sales = sales_df[sales_df['urun_id'] == urun['id']]
        
        if urun_sales.empty:
            predictions.append({
                'urun': urun['isim'],
                'kategori': urun['kategori'],
                'kalan_stok': urun['stok'],
                'minimum_stok': urun['minimum_stok'],
                'gunluk_ortalama': 0,
                'tahmini_gun': 'Tahmin yapılamaz',
                'durum': '🟡 Veri Yok'
            })
        else:
            # Son 30 günün ortalaması
            daily_sales = urun_sales.groupby('tarih')['adet'].sum()
            avg_daily = daily_sales.mean()
            
            if avg_daily > 0:
                tahmini_gun = int(urun['stok'] / avg_daily)
                
                # Durum belirleme
                if tahmini_gun <= 7:
                    durum = '🔴 Acil'
                elif tahmini_gun <= 14:
                    durum = '🟡 Dikkat'
                elif tahmini_gun <= 30:
                    durum = '🟢 Normal'
                else:
                    durum = '🟢 Güvenli'
                
                predictions.append({
                    'urun': urun['isim'],
                    'kategori': urun['kategori'],
                    'kalan_stok': urun['stok'],
                    'minimum_stok': urun['minimum_stok'],
                    'gunluk_ortalama': round(avg_daily, 2),
                    'tahmini_gun': tahmini_gun,
                    'durum': durum
                })
            else:
                predictions.append({
                    'urun': urun['isim'],
                    'kategori': urun['kategori'],
                    'kalan_stok': urun['stok'],
                    'minimum_stok': urun['minimum_stok'],
                    'gunluk_ortalama': 0,
                    'tahmini_gun': 'Tahmin yapılamaz',
                    'durum': '🟡 Veri Yok'
                })
    
    # Tahmin tablosu
    if predictions:
        # Filtreleme seçenekleri
        col1, col2 = st.columns(2)
        
        with col1:
            kategoriler = ["Tümü"] + list(set([p['kategori'] for p in predictions]))
            kategori_filter = st.selectbox("Kategori Filtresi", kategoriler)
        
        with col2:
            durum_filter = st.selectbox("Durum Filtresi", ["Tümü", "🔴 Acil", "🟡 Dikkat", "🟢 Normal", "🟢 Güvenli", "🟡 Veri Yok"])
        
        # Filtreleme uygula
        filtered_predictions = predictions
        if kategori_filter != "Tümü":
            filtered_predictions = [p for p in filtered_predictions if p['kategori'] == kategori_filter]
        
        if durum_filter != "Tümü":
            filtered_predictions = [p for p in filtered_predictions if p['durum'] == durum_filter]
        
        # Özet istatistikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            acil_urunler = len([p for p in predictions if p['durum'] == '🔴 Acil'])
            st.metric("Acil Ürünler", acil_urunler)
        
        with col2:
            dikkat_urunler = len([p for p in predictions if p['durum'] == '🟡 Dikkat'])
            st.metric("Dikkat Gereken", dikkat_urunler)
        
        with col3:
            normal_urunler = len([p for p in predictions if p['durum'] == '🟢 Normal'])
            st.metric("Normal", normal_urunler)
        
        with col4:
            toplam_urun = len(predictions)
            st.metric("Toplam Ürün", toplam_urun)
        
        st.markdown("---")
        
        # Tahmin tablosu
        st.write("### 📊 Stok Tükenme Tahmini")
        tahmin_df = pd.DataFrame(filtered_predictions)
        
        if not tahmin_df.empty:
            # Sütun isimlerini düzenle
            tahmin_df.columns = ['Ürün', 'Kategori', 'Kalan Stok', 'Min. Stok', 'Günlük Ortalama', 'Tahmini Gün', 'Durum']
            
            # Renklendirme fonksiyonu
            def color_status(val):
                if val == '🔴 Acil':
                    return 'background-color: #ffebee'
                elif val == '🟡 Dikkat':
                    return 'background-color: #fff3e0'
                elif val == '🟢 Normal':
                    return 'background-color: #e8f5e8'
                elif val == '🟢 Güvenli':
                    return 'background-color: #e8f5e8'
                else:
                    return 'background-color: #f5f5f5'
            
            st.dataframe(tahmin_df.style.applymap(color_status, subset=['Durum']), 
                        use_container_width=True, height=400)
            
            # Bar Chart: X=Ürün adı, Y=Tahmini kaç gün sonra stok tükenecek
            st.write("### 📈 Tahmini Stok Tükenme Süresi")
            valid_preds = [p for p in filtered_predictions if isinstance(p['tahmini_gun'], int)]
            
            if valid_preds:
                fig = go.Figure()
                
                # Renk kodlaması
                colors = []
                for p in valid_preds:
                    if p['durum'] == '🔴 Acil':
                        colors.append('red')
                    elif p['durum'] == '🟡 Dikkat':
                        colors.append('orange')
                    elif p['durum'] == '🟢 Normal':
                        colors.append('green')
                    else:
                        colors.append('lightgreen')
                
                fig.add_trace(go.Bar(
                    x=[p['urun'] for p in valid_preds],
                    y=[p['tahmini_gun'] for p in valid_preds],
                    text=[f"{p['tahmini_gun']} gün" for p in valid_preds],
                    textposition='auto',
                    marker_color=colors,
                ))
                
                fig.update_layout(
                    xaxis_title="Ürün",
                    yaxis_title="Tahmini Tükenme Süresi (Gün)",
                    title="Ürünlerin Tahmini Stok Tükenme Süresi",
                    showlegend=False,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Açıklama
                st.info("""
                **Durum Açıklamaları:**
                - 🔴 **Acil:** 7 gün veya daha az
                - 🟡 **Dikkat:** 8-14 gün arası
                - 🟢 **Normal:** 15-30 gün arası
                - 🟢 **Güvenli:** 30 günden fazla
                - 🟡 **Veri Yok:** Satış verisi bulunamadı
                """)
            else:
                st.info("Tahmin yapılabilen ürün bulunamadı.")
        else:
            st.info("Seçilen filtrelere uygun ürün bulunamadı.")
    else:
        st.info("Tahmin verisi bulunamadı.") 