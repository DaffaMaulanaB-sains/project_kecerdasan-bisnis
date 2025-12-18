# app.py (File Utama)
import streamlit as st

st.set_page_config(
    page_title="Dashboard Stunting Sidoarjo",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-text {
        text-align: center;
        font-size: 1.2rem;
        color: #555;
        padding: 1rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏥 Sistem Informasi Stunting Kabupaten Sidoarjo</div>', unsafe_allow_html=True)

st.markdown('<div class="welcome-text">Selamat datang di Dashboard Monitoring dan Analisis Data Stunting</div>', unsafe_allow_html=True)

st.markdown("---")

# Welcome content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Dashboard</h3>
        <p>Visualisasi data stunting secara keseluruhan dengan grafik dan statistik lengkap</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🗺️ Peta Sebaran</h3>
        <p>Peta interaktif sebaran kasus stunting di seluruh wilayah Sidoarjo</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Analisis</h3>
        <p>Analisis mendalam status gizi dan pertumbuhan balita</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Info section
st.markdown("### 📋 Tentang Sistem")
col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Tujuan Sistem:**
    - Monitoring kasus stunting real-time
    - Identifikasi wilayah prioritas
    - Analisis faktor risiko
    - Mendukung pengambilan keputusan
    """)

with col2:
    st.success("""
    **Fitur Utama:**
    - Filter data berdasarkan wilayah
    - Visualisasi interaktif
    - Export data CSV
    - Peta sebaran geografis
    """)

st.markdown("---")

# Instructions
st.markdown("### 🚀 Cara Menggunakan")
st.markdown("""
1. **Pilih Menu** di sidebar kiri sesuai kebutuhan analisis Anda
2. **Gunakan Filter** untuk menyaring data berdasarkan kecamatan, puskesmas, atau kriteria lain
3. **Lihat Visualisasi** untuk memahami pola dan tren data stunting
4. **Download Data** jika diperlukan untuk analisis lebih lanjut
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
    <p><strong>Dashboard Analisis Stunting Kabupaten Sidoarjo</strong></p>
    <p>Dinas Kesehatan Kabupaten Sidoarjo</p>
</div>
""", unsafe_allow_html=True)