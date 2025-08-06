import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import load_customers, save_customers

def calculate_rfm_scores(customers_df):
    """RFM skorlarını hesapla"""
    today = datetime.now()
    
    # Recency hesaplama (son alışverişten bu yana geçen gün)
    customers_df['son_satin_alma_tarihi'] = pd.to_datetime(customers_df['son_satin_alma_tarihi'])
    customers_df['recency'] = (today - customers_df['son_satin_alma_tarihi']).dt.days
    
    # RFM skorları (1-5 arası)
    # Recency: Düşük gün = Yüksek skor
    customers_df['R_score'] = pd.qcut(customers_df['recency'], q=5, labels=[5,4,3,2,1])
    
    # Frequency: Yüksek sayı = Yüksek skor
    customers_df['F_score'] = pd.qcut(customers_df['toplam_satin_alma_sayisi'], q=5, labels=[1,2,3,4,5])
    
    # Monetary: Yüksek harcama = Yüksek skor
    customers_df['M_score'] = pd.qcut(customers_df['toplam_harcama'], q=5, labels=[1,2,3,4,5])
    
    return customers_df

def segment_customers(customers_df):
    """Müşterileri segmentlere ayır"""
    def assign_segment(row):
        r_score = int(row['R_score'])
        f_score = int(row['F_score'])
        m_score = int(row['M_score'])
        
        # Segmentasyon kuralları
        if r_score >= 4 and f_score >= 4 and m_score >= 4:
            return "VIP Müşteriler"
        elif r_score >= 3 and f_score >= 3 and m_score >= 3:
            return "Sadık Müşteriler"
        elif r_score >= 3 and (f_score >= 3 or m_score >= 3):
            return "Aktif Müşteriler"
        elif r_score >= 2 and (f_score >= 2 or m_score >= 2):
            return "Orta Seviye Müşteriler"
        elif r_score >= 2:
            return "Risk Altındaki Müşteriler"
        else:
            return "Kayıp Müşteriler"
    
    def assign_recommendations(row):
        segment = row['Segment']
        if segment == "VIP Müşteriler":
            return "🎯 VIP hizmet, özel kampanyalar, erken erişim"
        elif segment == "Sadık Müşteriler":
            return "💎 Sadakat programı, özel indirimler"
        elif segment == "Aktif Müşteriler":
            return "📈 Daha fazla ürün önerisi, kampanyalar"
        elif segment == "Orta Seviye Müşteriler":
            return "📊 Kişiselleştirilmiş öneriler, e-posta kampanyaları"
        elif segment == "Risk Altındaki Müşteriler":
            return "⚠️ Yeniden aktifleştirme kampanyaları"
        elif segment == "Kayıp Müşteriler":
            return "🚨 Geri kazanım kampanyaları, özel teklifler"
        else:
            return "📋 Genel kampanyalar"
    
    customers_df['Segment'] = customers_df.apply(assign_segment, axis=1)
    customers_df['Öneriler'] = customers_df.apply(assign_recommendations, axis=1)
    return customers_df

def show_customer_segmentation():
    """Müşteri segmentasyonu sayfasını göster"""
    st.header("👥 Stockly Müşteri Analizi")
    st.markdown("Müşterilerinizi analiz edin ve segmentlere ayırın.")
    st.markdown("---")
    
    # Müşteri verilerini yükle
    customers_df = load_customers()
    
    if customers_df.empty:
        st.info("Müşteri verisi bulunamadı. Önce müşteri verilerini ekleyin.")
        return
    
    # RFM analizi yap
    customers_df = calculate_rfm_scores(customers_df)
    customers_df = segment_customers(customers_df)
    
    # Müşteri listesi - Büyük tablo
    st.write("### Müşteri Listesi ve Segment Analizi")
    display_df = customers_df[['musteri_adi', 'yas', 'cinsiyet', 'bolge', 'recency', 'toplam_satin_alma_sayisi', 'toplam_harcama', 'Segment', 'Öneriler']].copy()
    display_df.columns = ['Müşteri Adı', 'Yaş', 'Cinsiyet', 'Bölge', 'Son Alıştan Gün', 'Alışveriş Sayısı', 'Toplam Harcama (₺)', 'Segment', 'Öneriler']
    
    # Tabloyu büyüt ve scroll'u kaldır
    st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
        width: 100%;
    }
    .dataframe th {
        background-color: #f0f2f6;
        font-weight: bold;
        padding: 12px;
        text-align: center;
    }
    .dataframe td {
        padding: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Segment dağılımı
    st.write("### Segment Dağılımı")
    segment_counts = customers_df['Segment'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title="Müşteri Segment Dağılımı",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            x=segment_counts.index,
            y=segment_counts.values,
            title="Segment Bazında Müşteri Sayısı",
            color=segment_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # RFM Skorları Analizi
    st.write("### Müşteri Analizi Metrikleri")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ortalama Son Alıştan Gün", f"{customers_df['recency'].mean():.1f} gün")
        st.metric("Ortalama Alışveriş Sayısı", f"{customers_df['toplam_satin_alma_sayisi'].mean():.1f}")
    
    with col2:
        st.metric("Ortalama Toplam Harcama", f"{customers_df['toplam_harcama'].mean():.0f} ₺")
        st.metric("Toplam Müşteri", len(customers_df))
    
    with col3:
        st.metric("VIP Müşteri Sayısı", len(customers_df[customers_df['Segment'] == 'VIP Müşteriler']))
        st.metric("Kayıp Müşteri Sayısı", len(customers_df[customers_df['Segment'] == 'Kayıp Müşteriler']))
    
    # Segment bazında detaylı analiz
    st.write("### Segment Bazında Detaylı Analiz")
    
    for segment in customers_df['Segment'].unique():
        segment_data = customers_df[customers_df['Segment'] == segment]
        
        with st.expander(f"📊 {segment} ({len(segment_data)} müşteri)"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Ortalama Yaş", f"{segment_data['yas'].mean():.1f}")
                st.metric("Ortalama Harcama", f"{segment_data['toplam_harcama'].mean():.0f} ₺")
            
            with col2:
                st.metric("Ortalama Son Alıştan Gün", f"{segment_data['recency'].mean():.1f} gün")
                st.metric("Ortalama Alışveriş Sayısı", f"{segment_data['toplam_satin_alma_sayisi'].mean():.1f}")
            
            with col3:
                # Cinsiyet dağılımı
                gender_counts = segment_data['cinsiyet'].value_counts()
                st.write("**Cinsiyet Dağılımı:**")
                for gender, count in gender_counts.items():
                    st.write(f"- {gender}: {count}")
            
            # Bu segment için öneriler
            st.write("**Öneriler:**")
            if segment == "VIP Müşteriler":
                st.success("🎯 VIP hizmet, özel kampanyalar, erken erişim")
            elif segment == "Sadık Müşteriler":
                st.info("💎 Sadakat programı, özel indirimler")
            elif segment == "Aktif Müşteriler":
                st.warning("📈 Daha fazla ürün önerisi, kampanyalar")
            elif segment == "Orta Seviye Müşteriler":
                st.info("📊 Kişiselleştirilmiş öneriler, e-posta kampanyaları")
            elif segment == "Risk Altındaki Müşteriler":
                st.error("⚠️ Yeniden aktifleştirme kampanyaları")
            elif segment == "Kayıp Müşteriler":
                st.error("🚨 Geri kazanım kampanyaları, özel teklifler")
    
    # Bölge bazında analiz
    st.write("### Bölge Bazında Analiz")
    region_analysis = customers_df.groupby('bolge').agg({
        'musteri_adi': 'count',
        'toplam_harcama': 'mean',
        'toplam_satin_alma_sayisi': 'mean'
    }).round(2)
    
    region_analysis.columns = ['Müşteri Sayısı', 'Ortalama Harcama', 'Ortalama Satın Alma']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bölge bazında müşteri sayısı grafiği
        fig_customers = px.bar(
            x=region_analysis.index,
            y=region_analysis['Müşteri Sayısı'],
            title="Bölgelere Göre Müşteri Sayısı",
            color=region_analysis.index,
            color_discrete_sequence=px.colors.qualitative.Set1,
            text=region_analysis['Müşteri Sayısı']
        )
        fig_customers.update_layout(
            xaxis_title="Bölge",
            yaxis_title="Müşteri Sayısı",
            showlegend=False
        )
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with col2:
        # Bölge bazında ortalama harcama grafiği
        fig_spending = px.bar(
            x=region_analysis.index,
            y=region_analysis['Ortalama Harcama'],
            title="Bölgelere Göre Ortalama Harcama",
            color=region_analysis.index,
            color_discrete_sequence=px.colors.qualitative.Set2,
            text=region_analysis['Ortalama Harcama'].round(0).astype(str) + " ₺"
        )
        fig_spending.update_layout(
            xaxis_title="Bölge",
            yaxis_title="Ortalama Harcama (₺)",
            showlegend=False
        )
        st.plotly_chart(fig_spending, use_container_width=True)
    
    # Bölge analiz tablosu
    st.write("### Bölge Analiz Tablosu")
    st.dataframe(region_analysis, use_container_width=True) 