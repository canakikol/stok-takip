import streamlit as st
import pandas as pd
from utils import load_data, save_data, load_sales, save_sales, get_today

def show_sales_management():
    """Satış yönetimi sayfasını göster"""
    st.header("🛒 Stockly Satış Yönetimi")
    st.markdown("Ürün satışı ekleyin ve detaylı satış geçmişini görüntüleyin.")
    st.markdown("---")
    
    df = load_data()
    sales_df = load_sales()
    
    # Tab menüsü
    tab1, tab2, tab3 = st.tabs(["📝 Yeni Satış", "📊 Satış Geçmişi", "📈 Satış Analizi"])
    
    with tab1:
        show_new_sale_tab(df, sales_df)
    
    with tab2:
        show_sales_history_tab(df, sales_df)
    
    with tab3:
        show_sales_analytics_tab(df, sales_df)

def show_new_sale_tab(df, sales_df):
    """Yeni satış ekleme sekmesi"""
    st.write("### 📝 Yeni Satış Ekle")
    
    if df.empty:
        st.info("Satış eklemek için önce ürün eklemelisiniz.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # Kategori bazında ürün seçimi
            kategoriler = df['kategori'].unique().tolist()
            kategori_sec = st.selectbox("Kategori Seç", kategoriler)
            
            # Seçilen kategorideki ürünler
            kategori_urunleri = df[df['kategori'] == kategori_sec]
            urun_adlari = kategori_urunleri["isim"].tolist()
            urun_sec = st.selectbox("Ürün Seç", urun_adlari)
            
            if urun_sec:
                urun_row = df[df["isim"] == urun_sec].iloc[0]
                
                # Ürün bilgileri
                st.write("**Ürün Bilgileri:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Mevcut Stok", f"{urun_row['stok']} adet")
                    st.metric("Alış Fiyatı", f"{urun_row['alis_fiyati']} ₺")
                with col_b:
                    st.metric("Satış Fiyatı", f"{urun_row['satis_fiyati']} ₺")
                    kar_marji = ((urun_row['satis_fiyati'] - urun_row['alis_fiyati']) / urun_row['alis_fiyati'] * 100) if urun_row['alis_fiyati'] > 0 else 0
                    st.metric("Kar Marjı", f"%{kar_marji:.1f}")
        
        with col2:
            with st.form("Satış Ekle"):
                adet = st.number_input("Satılan Adet", min_value=1, max_value=int(urun_row["stok"]) if 'urun_row' in locals() else 1, step=1)
                fiyat = st.number_input("Satış Fiyatı (₺)", min_value=0.0, step=0.01, format="%.2f", 
                                      value=float(urun_row["satis_fiyati"]) if 'urun_row' in locals() else 0.0)
                
                # Otomatik hesaplamalar
                toplam_tutar = adet * fiyat
                kar_tutari = adet * (fiyat - urun_row['alis_fiyati']) if 'urun_row' in locals() else 0
                kar_yuzdesi = ((fiyat - urun_row['alis_fiyati']) / urun_row['alis_fiyati'] * 100) if 'urun_row' in locals() and urun_row['alis_fiyati'] > 0 else 0
                
                st.write("**Hesaplamalar:**")
                st.metric("Toplam Tutar", f"{toplam_tutar:.2f} ₺")
                st.metric("Kar Tutarı", f"{kar_tutari:.2f} ₺")
                st.metric("Kar Yüzdesi", f"%{kar_yuzdesi:.1f}")
                
                submitted = st.form_submit_button("✅ Satışı Kaydet")
                
                if submitted and 'urun_row' in locals():
                    if adet > urun_row["stok"]:
                        st.error("❌ Stokta yeterli ürün yok!")
                    else:
                        yeni_id = sales_df["id"].astype(float).max() + 1 if not sales_df.empty else 1
                        yeni_satis = pd.DataFrame([{
                            "id": yeni_id,
                            "urun_id": urun_row["id"],
                            "tarih": get_today(),
                            "adet": adet,
                            "fiyat": fiyat
                        }])
                        sales_df = pd.concat([sales_df, yeni_satis], ignore_index=True)
                        save_sales(sales_df)
                        
                        # Stok azalt
                        df.loc[df["id"] == urun_row["id"], "stok"] -= adet
                        save_data(df)
                        
                        st.success(f"✅ {adet} adet {urun_sec} satışı kaydedildi!")
                        st.info(f"💰 Toplam Tutar: {toplam_tutar:.2f} ₺")
                        st.info(f"📈 Kar: {kar_tutari:.2f} ₺ (%{kar_yuzdesi:.1f})")
                        st.rerun()

def show_sales_history_tab(df, sales_df):
    """Satış geçmişi sekmesi"""
    st.write("### 📊 Satış Geçmişi")
    
    if not sales_df.empty:
        # Veri birleştirme
        merged = sales_df.merge(df, left_on="urun_id", right_on="id", suffixes=("_satis", "_urun"))
        
        # Filtreleme seçenekleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            kategoriler = ["Tümü"] + merged['kategori'].unique().tolist()
            kategori_filter = st.selectbox("Kategori Filtresi", kategoriler)
        
        with col2:
            tarih_sirasi = st.selectbox("Tarih Sırası", ["En Yeni", "En Eski"])
        
        with col3:
            siralama = st.selectbox("Sıralama", ["Tarih", "Tutar", "Adet", "Ürün"])
        
        # Filtreleme uygula
        if kategori_filter != "Tümü":
            merged = merged[merged['kategori'] == kategori_filter]
        
        # Sıralama uygula
        if tarih_sirasi == "En Yeni":
            merged = merged.sort_values(by="tarih", ascending=False)
        else:
            merged = merged.sort_values(by="tarih", ascending=True)
        
        if siralama == "Tutar":
            merged = merged.sort_values(by="fiyat", ascending=False)
        elif siralama == "Adet":
            merged = merged.sort_values(by="adet", ascending=False)
        elif siralama == "Ürün":
            merged = merged.sort_values(by="isim")
        
        # Görüntülenecek sütunlar
        display_columns = ["tarih", "isim", "kategori", "adet", "fiyat", "alis_fiyati"]
        display_df = merged[display_columns].copy()
        
        # Toplam tutar ve kar hesaplama
        display_df['toplam_tutar'] = display_df['adet'] * display_df['fiyat']
        display_df['kar_tutari'] = display_df['adet'] * (display_df['fiyat'] - display_df['alis_fiyati'])
        display_df['kar_yuzdesi'] = ((display_df['fiyat'] - display_df['alis_fiyati']) / display_df['alis_fiyati'] * 100)
        
        # Sütun isimlerini düzenle
        display_df.columns = ['Tarih', 'Ürün', 'Kategori', 'Adet', 'Satış Fiyatı (₺)', 'Alış Fiyatı (₺)', 
                            'Toplam Tutar (₺)', 'Kar Tutarı (₺)', 'Kar Yüzdesi (%)']
        
        # Özet istatistikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            toplam_satis = len(display_df)
            st.metric("Toplam Satış", toplam_satis)
        
        with col2:
            toplam_tutar = display_df['Toplam Tutar (₺)'].sum()
            st.metric("Toplam Tutar", f"{toplam_tutar:.2f} ₺")
        
        with col3:
            toplam_kar = display_df['Kar Tutarı (₺)'].sum()
            st.metric("Toplam Kar", f"{toplam_kar:.2f} ₺")
        
        with col4:
            ortalama_kar = display_df['Kar Yüzdesi (%)'].mean()
            st.metric("Ortalama Kar %", f"%{ortalama_kar:.1f}")
        
        st.markdown("---")
        
        # Tablo gösterimi
        st.dataframe(display_df, use_container_width=True, height=400)
        
    else:
        st.info("Henüz satış kaydı yok.")

def show_sales_analytics_tab(df, sales_df):
    """Satış analizi sekmesi"""
    st.write("### 📈 Satış Analizi")
    
    if not sales_df.empty:
        merged = sales_df.merge(df, left_on="urun_id", right_on="id", suffixes=("_satis", "_urun"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Kategori Bazında Satışlar:**")
            kategori_satislari = merged.groupby('kategori').agg({
                'adet': 'sum',
                'fiyat': lambda x: (x * merged.loc[x.index, 'adet']).sum()
            }).reset_index()
            kategori_satislari.columns = ['Kategori', 'Toplam Adet', 'Toplam Tutar']
            st.dataframe(kategori_satislari, use_container_width=True)
        
        with col2:
            st.write("**En Çok Satan Ürünler:**")
            urun_satislari = merged.groupby('isim').agg({
                'adet': 'sum',
                'fiyat': lambda x: (x * merged.loc[x.index, 'adet']).sum()
            }).reset_index()
            urun_satislari.columns = ['Ürün', 'Toplam Adet', 'Toplam Tutar']
            urun_satislari = urun_satislari.sort_values('Toplam Adet', ascending=False).head(10)
            st.dataframe(urun_satislari, use_container_width=True)
        
        st.markdown("---")
        
        # Kar analizi
        st.write("**Kar Analizi:**")
        merged['kar_tutari'] = merged['adet'] * (merged['fiyat'] - merged['alis_fiyati'])
        merged['kar_yuzdesi'] = ((merged['fiyat'] - merged['alis_fiyati']) / merged['alis_fiyati'] * 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            toplam_kar = merged['kar_tutari'].sum()
            st.metric("Toplam Kar", f"{toplam_kar:.2f} ₺")
        
        with col2:
            ortalama_kar_yuzdesi = merged['kar_yuzdesi'].mean()
            st.metric("Ortalama Kar %", f"%{ortalama_kar_yuzdesi:.1f}")
        
        with col3:
            en_karli_urun = merged.loc[merged['kar_tutari'].idxmax(), 'isim']
            st.metric("En Karlı Ürün", en_karli_urun)
        
    else:
        st.info("Analiz için satış verisi yok.") 