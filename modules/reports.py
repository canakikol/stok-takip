import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

def show_reports():
    """Raporlar sayfasını göster"""
    st.header("📊 Stockly Raporları")
    st.markdown("Detaylı kar/zarar analizi ve stok raporları.")
    st.markdown("---")
    
    df = load_data()
    if df.empty:
        st.info("Raporlamak için ürün yok.")
    else:
        # Toplamlar
        toplam_stok = df["stok"].sum()
        toplam_alis = (df["stok"] * df["alis_fiyati"]).sum()
        toplam_satis = (df["stok"] * df["satis_fiyati"]).sum()
        toplam_kar = toplam_satis - toplam_alis

        st.metric("Toplam Stok", toplam_stok)
        st.metric("Toplam Alış Maliyeti", f"{toplam_alis:.2f} ₺")
        st.metric("Toplam Satış Potansiyeli", f"{toplam_satis:.2f} ₺")
        st.metric("Toplam Potansiyel Kar", f"{toplam_kar:.2f} ₺")

        # Kar oranı hesapla
        df["toplam_alis"] = df["stok"] * df["alis_fiyati"]
        df["toplam_satis"] = df["stok"] * df["satis_fiyati"]
        df["potansiyel_kar"] = df["toplam_satis"] - df["toplam_alis"]
        df["kar_orani"] = df.apply(
            lambda row: ((row["satis_fiyati"] - row["alis_fiyati"]) / row["alis_fiyati"] * 100) if row["alis_fiyati"] != 0 else 0,
            axis=1
        )
        
        st.write("### Ürün Bazında Kar/Zarar")
        st.dataframe(df[["isim", "stok", "alis_fiyati", "satis_fiyati", "toplam_alis", "toplam_satis", "potansiyel_kar", "kar_orani"]])

        st.markdown("---")
        st.write("### Stok Dağılımı (Adet)")
        fig1 = px.bar(df, x="isim", y="stok", color="isim", title="Stok Dağılımı", text="stok", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

        st.write("### Potansiyel Kar Dağılımı")
        fig2 = px.bar(df, x="isim", y="potansiyel_kar", color="isim", title="Potansiyel Kar", text="potansiyel_kar", color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig2, use_container_width=True)

        st.write("### Kar Oranı (%)")
        fig3 = px.bar(
            df,
            x="isim",
            y="kar_orani",
            color="isim",
            title="Ürün Bazında Kar Oranı (%)",
            text=df["kar_orani"].round(2).astype(str) + " %",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(yaxis_title="Kar Oranı (%)", xaxis_title="Ürün")
        st.plotly_chart(fig3, use_container_width=True) 