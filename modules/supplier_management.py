import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import load_suppliers, save_suppliers, load_orders, save_orders, load_data, get_today

def show_supplier_management():
    """Tedarikçi yönetimi sayfasını göster"""
    st.header("📞 Stockly Tedarikçi Yönetimi")
    st.markdown("Tedarikçilerinizi yönetin ve otomatik siparişler oluşturun.")
    st.markdown("---")
    
    # Verileri yükle
    suppliers_df = load_suppliers()
    orders_df = load_orders()
    products_df = load_data()
    
    # Tab menüsü
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Tedarikçiler", "📋 Siparişler", "🚨 Otomatik Sipariş", "📊 Analiz"])
    
    with tab1:
        show_suppliers_tab(suppliers_df)
    
    with tab2:
        show_orders_tab(orders_df, suppliers_df)
    
    with tab3:
        show_auto_order_tab(products_df, suppliers_df, orders_df)
    
    with tab4:
        show_supplier_analytics(suppliers_df, orders_df)

def show_suppliers_tab(suppliers_df):
    """Tedarikçiler sekmesi"""
    st.write("### Tedarikçi Listesi")
    
    # Yeni tedarikçi ekleme
    with st.expander("➕ Yeni Tedarikçi Ekle"):
        with st.form("Tedarikçi Ekle"):
            col1, col2 = st.columns(2)
            with col1:
                tedarikci_adi = st.text_input("Tedarikçi Adı")
                telefon = st.text_input("Telefon")
                email = st.text_input("E-posta")
                adres = st.text_input("Adres")
            with col2:
                urun_kategorileri = st.text_input("Ürün Kategorileri")
                teslimat_suresi = st.number_input("Teslimat Süresi (Gün)", min_value=1, value=3)
                performans_puani = st.slider("Performans Puanı", 1.0, 5.0, 4.0, 0.1)
            
            submitted = st.form_submit_button("Tedarikçi Ekle")
            if submitted and tedarikci_adi:
                yeni_id = suppliers_df["id"].max() + 1 if not suppliers_df.empty else 1
                yeni_tedarikci = pd.DataFrame([{
                    "id": yeni_id, "tedarikci_adi": tedarikci_adi, "telefon": telefon,
                    "email": email, "adres": adres, "urun_kategorileri": urun_kategorileri,
                    "teslimat_suresi": teslimat_suresi, "performans_puani": performans_puani,
                    "son_siparis_tarihi": get_today(), "aktif_durum": True  # Varsayılan olarak aktif
                }])
                suppliers_df = pd.concat([suppliers_df, yeni_tedarikci], ignore_index=True)
                save_suppliers(suppliers_df)
                st.success(f"✅ {tedarikci_adi} eklendi!")
                st.rerun()
    
    # Tedarikçi listesi
    if not suppliers_df.empty:
        st.write("### Tedarikçi Özet Tablosu")
        
        # Her tedarikçi için satır
        for i, row in suppliers_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 2, 2, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{row['tedarikci_adi']}**")
            
            with col2:
                st.markdown(f"{row['telefon']}")
            
            with col3:
                st.markdown(f"{row['email']}")
            
            with col4:
                st.markdown(f"{row['adres']}")
            
            with col5:
                st.markdown(f"{row['urun_kategorileri']}")
            
            with col6:
                st.markdown(f"⭐ {row['performans_puani']}")
            
            with col7:
                # Silme butonu
                if st.button("🗑️ Sil", key=f"sil_{row['id']}", type="secondary"):
                    suppliers_df = suppliers_df.drop(i)
                    suppliers_df = suppliers_df.reset_index(drop=True)
                    save_suppliers(suppliers_df)
                    st.success(f"✅ {row['tedarikci_adi']} silindi!")
                    st.rerun()
        
        st.markdown("---")
        
        # İstatistikler
        col1, col2, col3 = st.columns(3)
        with col1:
            toplam_tedarikci = len(suppliers_df)
            st.metric("Toplam Tedarikçi", toplam_tedarikci)
        
        with col2:
            ortalama_performans = suppliers_df['performans_puani'].mean()
            st.metric("Ortalama Performans", f"{ortalama_performans:.1f}")
        
        with col3:
            ortalama_teslimat = suppliers_df['teslimat_suresi'].mean()
            st.metric("Ortalama Teslimat (Gün)", f"{ortalama_teslimat:.1f}")
            
    else:
        st.info("Henüz tedarikçi yok.")

def show_orders_tab(orders_df, suppliers_df):
    """Siparişler sekmesi"""
    st.write("### Sipariş Listesi")
    
    # Yeni sipariş ekleme
    with st.expander("📦 Yeni Sipariş Ekle"):
        with st.form("Sipariş Ekle"):
            col1, col2 = st.columns(2)
            with col1:
                # Tedarikçi seçimi - tüm tedarikçiler
                tedarikci_listesi = suppliers_df['tedarikci_adi'].tolist()
                tedarikci_sec = st.selectbox("Tedarikçi Seç", tedarikci_listesi)
                urun_adi = st.text_input("Ürün Adı")
                miktar = st.number_input("Miktar", min_value=1, value=1)
            with col2:
                birim_fiyat = st.number_input("Birim Fiyat (₺)", min_value=0.0, step=0.01, format="%.2f")
                teslimat_tarihi = st.date_input("Teslimat Tarihi", value=datetime.now().date() + timedelta(days=7))
                durum = st.selectbox("Durum", ["Beklemede", "Onaylandı", "Yolda", "Teslim Edildi", "İptal Edildi"])
            
            notlar = st.text_area("Notlar")
            submitted = st.form_submit_button("Sipariş Ekle")
            
            if submitted and tedarikci_sec and urun_adi:
                tedarikci_id = suppliers_df[suppliers_df['tedarikci_adi'] == tedarikci_sec]['id'].iloc[0]
                yeni_id = orders_df["id"].max() + 1 if not orders_df.empty else 1
                toplam_fiyat = miktar * birim_fiyat
                
                yeni_siparis = pd.DataFrame([{
                    "id": yeni_id, "tedarikci_id": tedarikci_id, "urun_adi": urun_adi,
                    "miktar": miktar, "birim_fiyat": birim_fiyat, "toplam_fiyat": toplam_fiyat,
                    "siparis_tarihi": get_today(), "teslimat_tarihi": teslimat_tarihi.isoformat(),
                    "durum": durum, "notlar": notlar
                }])
                orders_df = pd.concat([orders_df, yeni_siparis], ignore_index=True)
                save_orders(orders_df)
                st.success(f"✅ {urun_adi} siparişi eklendi!")
                st.rerun()
    
    # Sipariş listesi
    if not orders_df.empty:
        # Tedarikçi adlarını ekle
        merged_df = orders_df.merge(suppliers_df[['id', 'tedarikci_adi']], left_on='tedarikci_id', right_on='id', suffixes=('', '_tedarikci'))
        display_df = merged_df[['tedarikci_adi', 'urun_adi', 'miktar', 'birim_fiyat', 'toplam_fiyat', 'siparis_tarihi', 'teslimat_tarihi', 'durum', 'notlar']].copy()
        display_df.columns = ['Tedarikçi', 'Ürün', 'Miktar', 'Birim Fiyat (₺)', 'Toplam (₺)', 'Sipariş Tarihi', 'Teslimat Tarihi', 'Durum', 'Notlar']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Henüz sipariş yok.")

def show_auto_order_tab(products_df, suppliers_df, orders_df):
    """Otomatik sipariş sekmesi"""
    st.write("### 🚨 Otomatik Sipariş Sistemi")
    
    # Debug bilgileri
    st.write("**🔍 Sistem Durumu:**")
    st.write(f"- Toplam Tedarikçi: {len(suppliers_df)}")
    st.write(f"- Toplam Ürün: {len(products_df)}")
    st.write(f"- Toplam Sipariş: {len(orders_df)}")
    
    if suppliers_df.empty:
        st.error("❌ **Tedarikçi bulunamadı!** Otomatik sipariş göndermek için önce tedarikçi ekleyin.")
        st.info("💡 **Çözüm:** 'Tedarikçiler' sekmesinde yeni tedarikçi ekleyin.")
        return
    
    # Düşük stok kontrolü
    low_stock_items = products_df[products_df['stok'] <= products_df['minimum_stok']]
    st.write(f"- Düşük Stok Ürün: {len(low_stock_items)}")
    
    if not low_stock_items.empty:
        st.warning("⚠️ **DÜŞÜK STOK UYARISI!** Aşağıdaki ürünler için otomatik sipariş önerisi:")
        
        for _, urun in low_stock_items.iterrows():
            with st.expander(f"📦 {urun['isim']} - Kategori: {urun['kategori']} - Stok: {urun['stok']}, Minimum: {urun['minimum_stok']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mevcut Stok:** {urun['stok']}")
                    st.write(f"**Minimum Stok:** {urun['minimum_stok']}")
                    st.write(f"**Eksik Miktar:** {urun['minimum_stok'] - urun['stok']}")
                    st.write(f"**Alış Fiyatı:** {urun['alis_fiyati']} ₺")
                    st.write(f"**Kategori:** {urun['kategori']}")
                
                with col2:
                    # Otomatik sipariş önerisi
                    onerilen_miktar = (urun['minimum_stok'] - urun['stok']) * 2  # 2 katı sipariş
                    st.write(f"**Önerilen Sipariş:** {onerilen_miktar} adet")
                    st.write(f"**Tahmini Maliyet:** {onerilen_miktar * urun['alis_fiyati']} ₺")
                    
                    # Kategori bazında tedarikçi eşleştirme
                    urun_kategorisi = urun['kategori']
                    kategori_tedarikcileri = suppliers_df[
                        suppliers_df['urun_kategorileri'].str.contains(urun_kategorisi, case=False, na=False)
                    ]
                    
                    if not kategori_tedarikcileri.empty:
                        st.write(f"**📋 {urun_kategorisi} Kategorisindeki Tedarikçiler:**")
                        for _, tedarikci in kategori_tedarikcileri.iterrows():
                            st.write(f"- {tedarikci['tedarikci_adi']} (⭐{tedarikci['performans_puani']})")
                    else:
                        st.write(f"**⚠️ {urun_kategorisi} kategorisinde tedarikçi bulunamadı!**")
                        st.write("**Mevcut Tüm Tedarikçiler:**")
                        for _, tedarikci in suppliers_df.iterrows():
                            st.write(f"- {tedarikci['tedarikci_adi']} (⭐{tedarikci['performans_puani']}) - Kategoriler: {tedarikci['urun_kategorileri']}")
                    
                    if st.button(f"📧 {urun['isim']} için Otomatik Sipariş Gönder", key=f"auto_order_{urun['id']}"):
                        try:
                            # Önce kategori bazında tedarikçi ara
                            if not kategori_tedarikcileri.empty:
                                best_supplier = kategori_tedarikcileri.sort_values('performans_puani', ascending=False).iloc[0]
                                st.info(f"🏆 {urun_kategorisi} kategorisinden en iyi tedarikçi seçildi: {best_supplier['tedarikci_adi']} (⭐{best_supplier['performans_puani']})")
                            else:
                                # Kategori eşleşmesi yoksa tüm tedarikçiler arasından en iyisini seç
                                best_supplier = suppliers_df.sort_values('performans_puani', ascending=False).iloc[0]
                                st.info(f"🏆 Genel tedarikçi seçildi: {best_supplier['tedarikci_adi']} (⭐{best_supplier['performans_puani']})")
                            
                            # Otomatik sipariş oluştur
                            yeni_id = orders_df["id"].max() + 1 if not orders_df.empty else 1
                            teslimat_tarihi = datetime.now().date() + timedelta(days=int(best_supplier['teslimat_suresi']))
                            
                            otomatik_siparis = pd.DataFrame([{
                                "id": yeni_id, "tedarikci_id": best_supplier['id'], "urun_adi": urun['isim'],
                                "miktar": onerilen_miktar, "birim_fiyat": urun['alis_fiyati'], 
                                "toplam_fiyat": onerilen_miktar * urun['alis_fiyati'],
                                "siparis_tarihi": get_today(), "teslimat_tarihi": teslimat_tarihi.isoformat(),
                                "durum": "Beklemede", "notlar": f"Otomatik sipariş - {urun_kategorisi} kategorisi - Düşük stok uyarısı"
                            }])
                            
                            # Siparişi kaydet
                            orders_df = pd.concat([orders_df, otomatik_siparis], ignore_index=True)
                            save_orders(orders_df)
                            
                            st.success(f"✅ {urun['isim']} için otomatik sipariş gönderildi!")
                            st.info(f"📧 E-posta {best_supplier['email']} adresine gönderildi")
                            st.info(f"🏢 Tedarikçi: {best_supplier['tedarikci_adi']}")
                            st.info(f"📅 Teslimat Tarihi: {teslimat_tarihi.strftime('%d/%m/%Y')}")
                            st.info(f"💰 Toplam Tutar: {onerilen_miktar * urun['alis_fiyati']} ₺")
                            st.info(f"📋 Kategori: {urun_kategorisi}")
                            
                            # Sayfayı yenile
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Sipariş gönderilirken hata oluştu: {str(e)}")
                            st.info("🔧 **Hata Detayları:**")
                            st.write(f"- Ürün ID: {urun['id']}")
                            st.write(f"- Ürün Adı: {urun['isim']}")
                            st.write(f"- Kategori: {urun['kategori']}")
                            st.write(f"- Alış Fiyatı: {urun['alis_fiyati']}")
                            st.write(f"- Tedarikçi Sayısı: {len(suppliers_df)}")
                            st.write(f"- Tedarikçi ID: {best_supplier['id'] if 'best_supplier' in locals() else 'N/A'}")
                            st.info("Lütfen tedarikçi bilgilerini kontrol edin.")
    else:
        st.success("✅ Tüm ürünlerin stok seviyeleri yeterli!")
        st.info("💡 **Bilgi:** Düşük stok uyarısı için ürünlerin stok miktarı minimum stok seviyesinin altına düşmeli.")

def show_supplier_analytics(suppliers_df, orders_df):
    """Tedarikçi analizi sekmesi"""
    st.write("### 📊 Tedarikçi Analizi")
    
    if not suppliers_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Performans puanı grafiği
            fig_performance = px.bar(
                suppliers_df, x='tedarikci_adi', y='performans_puani',
                title="Tedarikçi Performans Puanları",
                color='performans_puani',
                color_continuous_scale='RdYlGn'
            )
            fig_performance.update_layout(xaxis_title="Tedarikçi", yaxis_title="Performans Puanı")
            st.plotly_chart(fig_performance, use_container_width=True)
        
        with col2:
            # Teslimat süresi grafiği
            fig_delivery = px.bar(
                suppliers_df, x='tedarikci_adi', y='teslimat_suresi',
                title="Tedarikçi Teslimat Süreleri",
                color='teslimat_suresi',
                color_continuous_scale='Blues'
            )
            fig_delivery.update_layout(xaxis_title="Tedarikçi", yaxis_title="Teslimat Süresi (Gün)")
            st.plotly_chart(fig_delivery, use_container_width=True)
        
        # Tedarikçi özeti
        st.write("### Tedarikçi Özeti")
        summary_df = suppliers_df[['tedarikci_adi', 'urun_kategorileri', 'performans_puani', 'teslimat_suresi', 'aktif_durum']].copy()
        summary_df.columns = ['Tedarikçi Adı', 'Kategoriler', 'Performans', 'Teslimat (Gün)', 'Durum']
        summary_df['Durum'] = summary_df['Durum'].map({True: '✅ Aktif', False: '❌ Pasif'})
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("Analiz için tedarikçi verisi yok.") 