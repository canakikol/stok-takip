import streamlit as st
import pandas as pd
from utils import load_data, save_data, check_low_stock

def show_stock_management():
    """Stok yönetimi sayfasını göster"""
    st.header("📦 Stockly Stok Yönetimi")
    st.markdown("Ürünlerinizi ekleyin, düzenleyin ve stok durumlarını takip edin.")
    st.markdown("---")

    df = load_data()
    if not df.empty:
        low_stock_items = check_low_stock(df)
        if not low_stock_items.empty:
            st.warning("🚨 **DÜŞÜK STOK UYARISI!**")
            for _, item in low_stock_items.iterrows():
                st.error(f"⚠️ {item['isim']}: Stok {item['stok']}, Minimum {item['minimum_stok']} - Sipariş verilmesi gerekiyor!")
            st.markdown("---")

    with st.form("Ürün Ekle"):
        col1, col2 = st.columns(2)
        with col1:
            isim = st.text_input("Ürün Adı")
            stok = st.number_input("Stok Miktarı", min_value=0, value=0)
            alis_fiyati = st.number_input("Alış Fiyatı (₺)", min_value=0.0, step=0.01, format="%.2f")
        with col2:
            kategori = st.text_input("Kategori")
            minimum_stok = st.number_input("Minimum Stok", min_value=0, value=5)
            satis_fiyati = st.number_input("Satış Fiyatı (₺)", min_value=0.0, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("Ürün Ekle")
        if submitted and isim:
            yeni_id = df["id"].max() + 1 if not df.empty else 1
            yeni_urun = pd.DataFrame([{
                "id": yeni_id, "isim": isim, "kategori": kategori, "stok": stok,
                "alis_fiyati": alis_fiyati, "satis_fiyati": satis_fiyati, "minimum_stok": minimum_stok
            }])
            df = pd.concat([df, yeni_urun], ignore_index=True)
            save_data(df)
            st.success(f"✅ {isim} eklendi!")
            st.rerun()

    st.markdown("---")
    st.write("### Ürün Listesi")
    df = load_data()
    if not df.empty:
        df['stok_durumu'] = df.apply(
            lambda row: '🔴 DÜŞÜK STOK' if row['stok'] <= row['minimum_stok'] else '🟢 Normal',
            axis=1
        )
        display_df = df[['isim', 'kategori', 'stok', 'minimum_stok', 'alis_fiyati', 'satis_fiyati', 'stok_durumu']].copy()
        display_df.columns = ['Ürün', 'Kategori', 'Stok', 'Min. Stok', 'Alış Fiyatı', 'Satış Fiyatı', 'Durum']
        
        # CSS ile tablo stilini düzenle
        st.markdown("""
        <style>
        .dataframe {
            font-family: Arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }
        .dataframe th {
            background-color: #f0f2f6;
            color: #262730;
            font-weight: bold;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #e0e0e0;
        }
        .dataframe td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        .dataframe tr:hover {
            background-color: #f5f5f5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(display_df, use_container_width=True, height=400)
        low_stock_count = len(df[df['stok'] <= df['minimum_stok']])
        if low_stock_count > 0:
            st.warning(f"📊 **Özet:** {low_stock_count} ürün minimum stok seviyesinin altında!")
    else:
        st.info("Hiç ürün yok.")

    st.markdown("---")
    st.write("### Ürünleri Sil veya Güncelle")
    if not df.empty:
        for i, row in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([3, 2, 2, 2, 2, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{row['isim']}**")
            
            with col2:
                st.markdown(f"{row['kategori']}")
            
            with col3:
                st.markdown(f"{row['stok']}")
            
            with col4:
                st.markdown(f"{row['alis_fiyati']} ₺")
            
            with col5:
                st.markdown(f"{row['satis_fiyati']} ₺")
            
            with col6:
                if row['stok'] <= row['minimum_stok']:
                    st.markdown("🔴 **DÜŞÜK**")
                else:
                    st.markdown("🟢 **Normal**")
            
            with col7:
                if st.button("✏️ Güncelle", key=f"guncelle_{row['id']}", type="secondary"):
                    st.session_state.guncellenecek_id = row['id']
                    st.rerun()
            
            with col8:
                if st.button("🗑️ Sil", key=f"sil_{row['id']}", type="secondary"):
                    df = df.drop(i)
                    df = df.reset_index(drop=True)
                    save_data(df)
                    st.success(f"✅ {row['isim']} silindi!")
                    st.rerun()
    else:
        st.info("Hiç ürün yok.")

    if "guncellenecek_id" in st.session_state:
        guncellenecek_urun = df[df['id'] == st.session_state.guncellenecek_id].iloc[0]
        st.markdown("---")
        st.write("### Ürün Güncelle")
        with st.form("Ürün Güncelle"):
            col1, col2 = st.columns(2)
            with col1:
                yeni_isim = st.text_input("Ürün Adı", value=guncellenecek_urun['isim'])
                yeni_stok = st.number_input("Stok Miktarı", min_value=0, value=int(guncellenecek_urun['stok']))
                yeni_alis_fiyati = st.number_input("Alış Fiyatı (₺)", min_value=0.0, step=0.01, format="%.2f", value=float(guncellenecek_urun['alis_fiyati']))
            with col2:
                yeni_kategori = st.text_input("Kategori", value=guncellenecek_urun['kategori'])
                yeni_minimum_stok = st.number_input("Minimum Stok", min_value=0, value=int(guncellenecek_urun['minimum_stok']))
                yeni_satis_fiyati = st.number_input("Satış Fiyatı (₺)", min_value=0.0, step=0.01, format="%.2f", value=float(guncellenecek_urun['satis_fiyati']))
            
            submitted = st.form_submit_button("Güncelle")
            if submitted:
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'isim'] = yeni_isim
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'kategori'] = yeni_kategori
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'stok'] = yeni_stok
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'alis_fiyati'] = yeni_alis_fiyati
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'satis_fiyati'] = yeni_satis_fiyati
                df.loc[df['id'] == st.session_state.guncellenecek_id, 'minimum_stok'] = yeni_minimum_stok
                save_data(df)
                st.success(f"✅ {yeni_isim} güncellendi!")
                del st.session_state.guncellenecek_id
                st.rerun() 