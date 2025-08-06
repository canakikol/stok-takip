import streamlit as st
from modules.stock_management import show_stock_management
from modules.sales_management import show_sales_management
from modules.reports import show_reports
from modules.ai_predictions import show_ai_predictions
from modules.customer_segmentation import show_customer_segmentation
from modules.supplier_management import show_supplier_management

# --- SIDEBAR ---
st.sidebar.image("https://em-content.zobj.net/source/microsoft-teams/363/package_1f4e6.png", width=60)
st.sidebar.title("Stockly")
st.sidebar.markdown("Küçük işletmeler için büyük kontrol.\n\n:bulb: **AI destekli stok yönetimi**")

menu = st.sidebar.selectbox("Menü", ["📦 Stok Yönetimi", "📊 Raporlar", "🛒 Satışlar", "🤖 AI Modülleri", "👥 Müşteri Segmentasyonu", "📞 Tedarikçi Yönetimi"])

# --- ANA SAYFA ---
st.title("📦 Stockly")
st.markdown("# **Küçük işletmeler için büyük kontrol**")
st.markdown("KOBİ'ler için kolay, hızlı ve akıllı stok yönetimi uygulaması.")

# Menü yönlendirmeleri
if menu == "📦 Stok Yönetimi":
    show_stock_management()
elif menu == "📊 Raporlar":
    show_reports()
elif menu == "🛒 Satışlar":
    show_sales_management()
elif menu == "🤖 AI Modülleri":
    show_ai_predictions()
elif menu == "👥 Müşteri Segmentasyonu":
    show_customer_segmentation()
elif menu == "📞 Tedarikçi Yönetimi":
    show_supplier_management()