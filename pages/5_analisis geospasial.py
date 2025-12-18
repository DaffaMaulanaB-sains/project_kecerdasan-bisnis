import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
from esda.getisord import G_Local
import warnings
warnings.filterwarnings("ignore")

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Analisis Geospasial Stunting",
    page_icon="🗺️",
    layout="wide"
)

# ======================================================
# ENHANCED STYLE
# ======================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .header-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 3.5rem 2rem;
        border-radius: 2.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 25px 70px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
        animation: slideDown 0.8s ease-out;
        border: 3px solid rgba(255,255,255,0.2);
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .header-box h1 {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 5px 5px 15px rgba(0,0,0,0.6);
        letter-spacing: -1.5px;
        line-height: 1.2;
    }
    
    .header-box p {
        font-size: 1.4rem;
        margin-top: 1.2rem;
        opacity: 0.95;
        font-weight: 500;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 2rem;
        border-radius: 1.5rem;
        border-left: 8px solid #1e88e5;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        animation: fadeInUp 1s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .info-box b {
        color: #0d47a1;
        font-size: 1.15rem;
        font-weight: 700;
    }
    
    /* Metric Card Styling */
    .stMetric {
        background: white;
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
    }
    
    .stMetric:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border-color: #667eea;
    }
    
    .stMetric label {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #546e7a !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Section Headers */
    h2, h3 {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 1.2rem;
        margin: 2.5rem 0 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-left: 8px solid #667eea;
        color: #2c3e50;
        font-weight: 800;
    }
    
    /* Success/Info/Warning Messages */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 1.2rem !important;
        padding: 1.5rem !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1) !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-left: 6px solid #28a745 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-left: 6px solid #17a2b8 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%) !important;
        border-left: 6px solid #ffc107 !important;
    }
    
    /* Plotly Chart Container */
    .js-plotly-plot {
        border-radius: 1.5rem;
        overflow: hidden;
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        background: white;
        padding: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Caption Styling */
    .stCaption {
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #ffc107;
        margin-top: 1.5rem;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Markdown List Styling */
    .main ul, .main ol {
        background: white;
        padding: 1.5rem 2rem 1.5rem 3rem;
        border-radius: 1rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .main li {
        margin: 0.8rem 0;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .main strong {
        color: #667eea;
        font-weight: 700;
    }
    
    /* Divider */
    hr {
        margin: 3rem 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        border: none;
        border-radius: 2px;
    }
    
    /* Insights Box */
    .insight-box {
        background: white;
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin: 2rem 0;
        border-top: 6px solid #667eea;
    }
    
    .insight-box h4 {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 0;
        margin-bottom: 1rem;
    }
    
    .stat-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 2rem;
        font-weight: 700;
        margin: 0.3rem;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        font-size: 1rem;
    }
    
    /* Loading Animation */
    .stSpinner > div {
        border-color: #667eea !important;
        border-right-color: transparent !important;
    }
    
    /* Legend Items */
    .legend-container {
        background: white;
        padding: 2rem;
        border-radius: 1.2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        margin: 1.5rem 0;
    }
    
    .legend-item {
        display: inline-flex;
        align-items: center;
        margin: 0.6rem 1rem;
        padding: 0.8rem 1.5rem;
        background: #f8f9fa;
        border-radius: 1rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        font-weight: 600;
        transition: transform 0.2s ease;
    }
    
    .legend-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    
    .legend-color {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        margin-right: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================
st.markdown("""
<div class="header-box">
    <h1>🗺️ Analisis Geospasial Stunting<br>Kabupaten Sidoarjo</h1>
    <p>Moran's I • LISA • Hotspot Analysis (Getis-Ord Gi*)</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<b>📌 Catatan Penting:</b><br>
Ringkasan data dihitung dari <b>data individu balita</b>, 
sedangkan analisis spasial dilakukan pada <b>tingkat desa</b>
yang memiliki hubungan spasial (tetangga geografis).
</div>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    DATA_DIR = Path("data")
    df = pd.read_csv(DATA_DIR / "data_skrinning_stunting(1).csv")
    gdf = gpd.read_file(DATA_DIR / "peta_sidoarjo.geojson")
    return df, gdf

with st.spinner("🔄 Memuat dan memproses data..."):
    df, gdf = load_data()

# ======================================================
# RINGKASAN DATA
# ======================================================
st.markdown("## 📊 Ringkasan Data Keseluruhan")

total_balita = len(df)
total_stunting = (df["stunting_balita"] == "Ya").sum()
rata_prevalensi = (total_stunting / total_balita) * 100
jumlah_desa = df["nama_desa"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("👶 Total Balita", f"{total_balita:,}")
c2.metric("⚠️ Kasus Stunting", f"{total_stunting:,}")
c3.metric("📈 Rata-rata Prevalensi", f"{rata_prevalensi:.2f}%")
c4.metric("📍 Jumlah Desa", f"{jumlah_desa}")

st.markdown("---")

# ======================================================
# DETEKSI KOLOM NAMA DESA PADA PETA
# ======================================================
desa_col = next(
    c for c in ["WADMKD","wadmkd","NAMA_DESA","nama_desa","DESA","desa","NAMOBJ"]
    if c in gdf.columns
)

# ======================================================
# AGREGASI DATA PER DESA
# ======================================================
df["desa_norm"] = df["nama_desa"].astype(str).str.lower().str.strip()
gdf[desa_col] = gdf[desa_col].astype(str).str.lower().str.strip()

df["stunting_flag"] = (df["stunting_balita"] == "Ya").astype(int)

agg = df.groupby("desa_norm").agg(
    total=("stunting_flag", "count"),
    kasus=("stunting_flag", "sum")
).reset_index()

agg["prevalensi"] = (agg["kasus"] / agg["total"] * 100).round(2)

gdf = gdf.merge(
    agg,
    left_on=desa_col,
    right_on="desa_norm",
    how="left"
)

gdf[["kasus","total","prevalensi"]] = gdf[
    ["kasus","total","prevalensi"]
].fillna(0)

try:
    gdf = gdf.to_crs(4326)
except:
    pass

# ======================================================
# SPATIAL WEIGHTS
# ======================================================
w = Queen.from_dataframe(gdf)
islands = list(w.islands)

if islands:
    gdf_spatial = gdf.drop(index=islands).copy()
else:
    gdf_spatial = gdf.copy()

w = Queen.from_dataframe(gdf_spatial)
w.transform = "r"
y = gdf_spatial["prevalensi"].values

# ======================================================
# MORAN'S I
# ======================================================
st.markdown("## 🌐 Moran's I - Autokorelasi Spasial Global")

st.markdown("""
<div class="insight-box">
<h4>📚 Tentang Moran's I</h4>
<p><b>Moran's I</b> mengukur seberapa mirip nilai prevalensi stunting di suatu desa dengan desa-desa tetangganya.</p>
<ul style="margin-left: 1rem;">
<li>📈 <b>I > 0:</b> Pola clustering (desa dengan nilai mirip cenderung berdekatan)</li>
<li>📉 <b>I < 0:</b> Pola dispersed (desa dengan nilai berbeda cenderung berdekatan)</li>
<li>➖ <b>I ≈ 0:</b> Pola random (tidak ada korelasi spasial)</li>
</ul>
<p><b>Interpretasi p-value:</b> Jika p < 0.05, maka pola spasial signifikan secara statistik.</p>
</div>
""", unsafe_allow_html=True)

moran = Moran(y, w)

c1, c2, c3 = st.columns(3)
c1.metric("Moran's I", f"{moran.I:.4f}", help="Nilai autokorelasi spasial")
c2.metric("P-Value", f"{moran.p_sim:.4f}", help="Tingkat signifikansi statistik")
c3.metric("Z-Score", f"{moran.z_sim:.3f}", help="Standar deviasi dari expected value")

if moran.p_sim < 0.05:
    if moran.I > 0:
        st.success(f"""
✅ **Terdapat autokorelasi spasial global yang signifikan!**

Moran's I = {moran.I:.4f} (p = {moran.p_sim:.4f})

**Artinya:** Desa dengan prevalensi stunting tinggi cenderung berdekatan dengan desa prevalensi tinggi lainnya. 
Ini mengindikasikan adanya pola clustering yang kuat. Faktor geografis, lingkungan, atau sosial-ekonomi 
kemungkinan berperan dalam distribusi stunting.

**Implikasi:** Program intervensi sebaiknya menggunakan pendekatan berbasis area/cluster untuk efektivitas maksimal.
        """)
    else:
        st.warning(f"""
⚠️ **Terdapat autokorelasi spasial negatif yang signifikan!**

Moran's I = {moran.I:.4f} (p = {moran.p_sim:.4f})

**Artinya:** Desa dengan prevalensi tinggi cenderung bertetangga dengan desa prevalensi rendah (pola checkerboard).
        """)
else:
    st.info(f"""
ℹ️ **Tidak ditemukan autokorelasi spasial global yang signifikan.**

Moran's I = {moran.I:.4f} (p = {moran.p_sim:.4f})

**Artinya:** Secara global, distribusi stunting bersifat random. Namun **analisis lokal (LISA dan Hotspot) 
tetap penting** karena bisa ada cluster lokal yang signifikan meskipun pola global tidak terdeteksi.
    """)

# Moran Scatter Plot
st.markdown("### 📊 Moran Scatter Plot")

gdf_spatial['lag_prevalensi'] = w.sparse.dot(y)

fig_scatter = px.scatter(
    gdf_spatial,
    x='prevalensi',
    y='lag_prevalensi',
    hover_name=desa_col,
    hover_data={'prevalensi': ':.2f', 'lag_prevalensi': ':.2f', 'kasus': True},
    labels={
        'prevalensi': 'Prevalensi Lokal (%)',
        'lag_prevalensi': 'Rata-rata Prevalensi Tetangga (%)'
    },
    title='Hubungan Prevalensi Lokal dengan Tetangga',
    template='plotly_white',
    color_discrete_sequence=['#667eea']
)

# Add trend line
z = np.polyfit(gdf_spatial['prevalensi'], gdf_spatial['lag_prevalensi'], 1)
p = np.poly1d(z)
x_line = np.linspace(gdf_spatial['prevalensi'].min(), gdf_spatial['prevalensi'].max(), 100)

fig_scatter.add_trace(
    go.Scatter(
        x=x_line,
        y=p(x_line),
        mode='lines',
        line=dict(color='#f5576c', dash='dash', width=3),
        name='Trend Line'
    )
)

# Add quadrant lines
mean_prev = gdf_spatial['prevalensi'].mean()
mean_lag = gdf_spatial['lag_prevalensi'].mean()

fig_scatter.add_hline(y=mean_lag, line_dash="dot", line_color="gray", opacity=0.5)
fig_scatter.add_vline(x=mean_prev, line_dash="dot", line_color="gray", opacity=0.5)

fig_scatter.update_layout(
    height=500,
    title_x=0.5,
    title_font_size=18,
    showlegend=True
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ======================================================
# LISA MAP
# ======================================================
st.markdown("## 🧩 LISA Map - Klaster Spasial Lokal")

st.markdown("""
<div class="insight-box">
<h4>📚 Tentang LISA (Local Indicators of Spatial Association)</h4>
<p>LISA mengidentifikasi cluster spasial lokal yang signifikan:</p>
<ul style="margin-left: 1rem;">
<li>🔴 <b>High-High:</b> Hotspot - desa dengan prevalensi tinggi dikelilingi desa prevalensi tinggi</li>
<li>🔵 <b>Low-Low:</b> Coldspot - desa dengan prevalensi rendah dikelilingi desa prevalensi rendah</li>
<li>🟠 <b>High-Low:</b> Outlier - desa prevalensi tinggi di area prevalensi rendah</li>
<li>🔷 <b>Low-High:</b> Outlier - desa prevalensi rendah di area prevalensi tinggi</li>
<li>⚪ <b>Tidak Signifikan:</b> Tidak ada pola lokal yang signifikan</li>
</ul>
</div>
""", unsafe_allow_html=True)

lisa = Moran_Local(y, w)

gdf_spatial["lisa_cluster"] = "Tidak Signifikan"
sig = lisa.p_sim < 0.05

gdf_spatial.loc[(lisa.q==1)&sig,"lisa_cluster"]="High-High"
gdf_spatial.loc[(lisa.q==3)&sig,"lisa_cluster"]="Low-Low"
gdf_spatial.loc[(lisa.q==2)&sig,"lisa_cluster"]="Low-High"
gdf_spatial.loc[(lisa.q==4)&sig,"lisa_cluster"]="High-Low"

# Count clusters
hh = (gdf_spatial["lisa_cluster"]=="High-High").sum()
ll = (gdf_spatial["lisa_cluster"]=="Low-Low").sum()
hl = (gdf_spatial["lisa_cluster"]=="High-Low").sum()
lh = (gdf_spatial["lisa_cluster"]=="Low-High").sum()
ns = (gdf_spatial["lisa_cluster"]=="Tidak Signifikan").sum()

# Display stats
st.markdown(f"""
<div style="text-align: center; margin: 1.5rem 0;">
    <span class="stat-badge" style="background: linear-gradient(135deg, #b2182b 0%, #d32f2f 100%);">🔴 High-High: {hh}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #2166ac 0%, #1565c0 100%);">🔵 Low-Low: {ll}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #ef8a62 0%, #ff7043 100%);">🟠 High-Low: {hl}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #67a9cf 0%, #4fc3f7 100%);">🔷 Low-High: {lh}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%);">⚪ Not Sig: {ns}</span>
</div>
""", unsafe_allow_html=True)

fig_lisa = px.choropleth(
    gdf_spatial,
    geojson=gdf_spatial.geometry,
    locations=gdf_spatial.index,
    color="lisa_cluster",
    hover_name=desa_col,
    hover_data={"prevalensi":":.2f","kasus":True,"total":True},
    color_discrete_map={
        "High-High":"#b2182b",
        "Low-Low":"#2166ac",
        "High-Low":"#ef8a62",
        "Low-High":"#67a9cf",
        "Tidak Signifikan":"#e0e0e0"
    },
    category_orders={
        "lisa_cluster": ["High-High", "Low-Low", "High-Low", "Low-High", "Tidak Signifikan"]
    },
    height=700,
    title="LISA Cluster Map - Pola Spasial Lokal Stunting"
)

fig_lisa.update_geos(fitbounds="locations", visible=False)
fig_lisa.update_layout(
    title_x=0.5,
    title_font_size=20,
    title_font_weight="bold"
)

st.plotly_chart(fig_lisa, use_container_width=True)

# Legend
st.markdown("""
<div class="legend-container">
    <h4 style="color: #667eea; margin-top: 0;">🎨 Interpretasi Warna Peta</h4>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <div class="legend-item">
            <span class="legend-color" style="background: #b2182b;"></span>
            <strong>High-High:</strong> Area prioritas utama (hotspot cluster)
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #2166ac;"></span>
            <strong>Low-Low:</strong> Area best practice (coldspot cluster)
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #ef8a62;"></span>
            <strong>High-Low:</strong> Outlier yang perlu investigasi khusus
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #67a9cf;"></span>
            <strong>Low-High:</strong> Desa yang berhasil di area berisiko
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #e0e0e0;"></span>
            <strong>Tidak Signifikan:</strong> Pola acak
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if hh > 0:
    high_high_desa = gdf_spatial[gdf_spatial["lisa_cluster"]=="High-High"]
    st.warning(f"""
🔴 **HOTSPOT CLUSTER TERIDENTIFIKASI ({hh} desa)**

Desa-desa berikut membentuk cluster hotspot dengan prevalensi stunting tinggi:

{', '.join(['**' + str(d).upper() + '**' for d in high_high_desa[desa_col].tolist()])}

**Rekomendasi:**
- Prioritaskan intervensi di cluster ini
- Gunakan pendekatan area-based untuk efisiensi
- Identifikasi faktor lingkungan/sosial penyebab clustering
- Koordinasi lintas desa dalam cluster sangat penting
    """)

if ll > 0:
    low_low_desa = gdf_spatial[gdf_spatial["lisa_cluster"]=="Low-Low"]
    st.success(f"""
🔵 **BEST PRACTICE AREA ({ll} desa)**

Desa-desa berikut membentuk cluster dengan prevalensi stunting rendah:

{', '.join(['**' + str(d).upper() + '**' for d in low_low_desa[desa_col].tolist()])}

**Rekomendasi:**
- Pelajari program/praktik terbaik di cluster ini
- Transfer knowledge ke area hotspot
- Pertahankan program yang sudah berjalan baik
    """)

st.markdown("---")

# ======================================================
# HOTSPOT ANALYSIS
# ======================================================
st.markdown("## 🔥 Hotspot Analysis - Getis-Ord Gi*")

st.markdown("""
<div class="insight-box">
<h4>📚 Tentang Hotspot Analysis (Getis-Ord Gi*)</h4>
<p>Getis-Ord Gi* mengidentifikasi cluster dengan menggunakan z-score untuk menentukan apakah suatu area 
memiliki konsentrasi nilai tinggi atau rendah yang signifikan secara statistik.</p>
<ul style="margin-left: 1rem;">
<li>🔥 <b>Hotspot:</b> Area dengan nilai tinggi yang dikelilingi nilai tinggi lainnya (Z > 1.96, p < 0.05)</li>
<li>❄️ <b>Coldspot:</b> Area dengan nilai rendah yang dikelilingi nilai rendah lainnya (Z < -1.96, p < 0.05)</li>
<li>⚪ <b>Tidak Signifikan:</b> Tidak ada pola clustering yang signifikan</li>
</ul>
</div>
""", unsafe_allow_html=True)

gi = G_Local(y, w)

gdf_spatial["hotspot"] = "Tidak Signifikan"
gdf_spatial.loc[(gi.Zs > 1.96) & (gi.p_sim < 0.05),"hotspot"]="Hotspot"
gdf_spatial.loc[(gi.Zs < -1.96) & (gi.p_sim < 0.05),"hotspot"]="Coldspot"

# Count hotspots
n_hot = (gdf_spatial["hotspot"]=="Hotspot").sum()
n_cold = (gdf_spatial["hotspot"]=="Coldspot").sum()
n_ns = (gdf_spatial["hotspot"]=="Tidak Signifikan").sum()

st.markdown(f"""
<div style="text-align: center; margin: 1.5rem 0;">
    <span class="stat-badge" style="background: linear-gradient(135deg, #cb181d 0%, #a50f15 100%);">🔥 Hotspot: {n_hot}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #2171b5 0%, #08519c 100%);">❄️ Coldspot: {n_cold}</span>
    <span class="stat-badge" style="background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%);">⚪ Not Significant: {n_ns}</span>
</div>
""", unsafe_allow_html=True)

fig_hot = px.choropleth(
    gdf_spatial,
    geojson=gdf_spatial.geometry,
    locations=gdf_spatial.index,
    color="hotspot",
    hover_name=desa_col,
    hover_data={"prevalensi":":.2f","kasus":True,"total":True},
    color_discrete_map={
        "Hotspot":"#cb181d",
        "Coldspot":"#2171b5",
        "Tidak Signifikan":"#f0f0f0"
    },
    category_orders={
        "hotspot": ["Hotspot", "Coldspot", "Tidak Signifikan"]
    },
    height=700,
    title="Hotspot Analysis Map - Getis-Ord Gi* Stunting"
)

fig_hot.update_geos(fitbounds="locations", visible=False)
fig_hot.update_layout(
    title_x=0.5,
    title_font_size=20,
    title_font_weight="bold"
)

st.plotly_chart(fig_hot, use_container_width=True)

# Legend
st.markdown("""
<div class="legend-container">
    <h4 style="color: #667eea; margin-top: 0;">🎨 Interpretasi Warna Peta</h4>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <div class="legend-item">
            <span class="legend-color" style="background: #cb181d;"></span>
            <strong>Hotspot:</strong> Konsentrasi prevalensi tinggi yang signifikan
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #2171b5;"></span>
            <strong>Coldspot:</strong> Konsentrasi prevalensi rendah yang signifikan
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #f0f0f0;"></span>
            <strong>Tidak Signifikan:</strong> Tidak ada pola clustering
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if n_hot > 0:
    hotspot_desa = gdf_spatial[gdf_spatial["hotspot"]=="Hotspot"]
    hotspot_names = ', '.join(['**' + str(d).upper() + '**' for d in hotspot_desa[desa_col].tolist()])
    avg_prev_hotspot = hotspot_desa['prevalensi'].mean()
    total_kasus_hotspot = hotspot_desa['kasus'].sum()
    
    st.warning(f"""
🔥 **AREA HOTSPOT TERIDENTIFIKASI ({n_hot} desa)**

**Desa-desa hotspot:** {hotspot_names}

**Statistik Hotspot:**
- Rata-rata prevalensi di hotspot: **{avg_prev_hotspot:.2f}%**
- Total kasus stunting di hotspot: **{int(total_kasus_hotspot)} kasus**
- Persentase dari total kasus: **{(total_kasus_hotspot/total_stunting*100):.1f}%**

**🎯 Rekomendasi Prioritas:**
1. **Intervensi Segera:** Fokuskan program stunting di {n_hot} desa hotspot ini
2. **Investigasi Mendalam:** Identifikasi faktor risiko spesifik di area hotspot
3. **Mobilisasi Sumber Daya:** Alokasikan tim kesehatan dan anggaran prioritas
4. **Monitoring Intensif:** Evaluasi berkala setiap bulan untuk tracking progress
    """)

if n_cold > 0:
    coldspot_desa = gdf_spatial[gdf_spatial["hotspot"]=="Coldspot"]
    coldspot_names = ', '.join(['**' + str(d).upper() + '**' for d in coldspot_desa[desa_col].tolist()])
    avg_prev_coldspot = coldspot_desa['prevalensi'].mean()
    
    st.success(f"""
❄️ **AREA COLDSPOT (BEST PRACTICE) - {n_cold} desa**

**Desa-desa coldspot:** {coldspot_names}

**Statistik Coldspot:**
- Rata-rata prevalensi di coldspot: **{avg_prev_coldspot:.2f}%**

**✨ Rekomendasi Best Practice:**
1. **Studi Kasus:** Dokumentasikan program/strategi yang berhasil
2. **Knowledge Sharing:** Gelar workshop transfer pengetahuan ke desa lain
3. **Maintenance:** Pertahankan dan tingkatkan program yang sudah berjalan
4. **Replikasi:** Terapkan model sukses ke area hotspot
    """)

st.markdown("---")

# ======================================================
# KESIMPULAN
# ======================================================
st.markdown("## 🧠 Kesimpulan & Rekomendasi Strategis")

st.markdown(f"""
<div class="insight-box">
<h4>📋 Ringkasan Temuan Analisis Geospasial</h4>

<b>1. Data Keseluruhan:</b>
- Total balita yang dianalisis: <b>{total_balita:,} balita</b>
- Total kasus stunting: <b>{total_stunting:,} kasus ({rata_prevalensi:.2f}%)</b>
- Jumlah desa: <b>{jumlah_desa} desa</b>

<b>2. Analisis Autokorelasi Spasial Global (Moran's I):</b>
- Moran's I = <b>{moran.I:.4f}</b> (p-value = {moran.p_sim:.4f})
- Status: <b>{"Signifikan" if moran.p_sim < 0.05 else "Tidak Signifikan"}</b>
- Pola: <b>{"Clustering" if moran.I > 0 and moran.p_sim < 0.05 else "Random/Dispersed"}</b>

<b>3. LISA Cluster Map:</b>
- Hotspot Cluster (High-High): <b>{hh} desa</b>
- Coldspot Cluster (Low-Low): <b>{ll} desa</b>
- Outlier High-Low: <b>{hl} desa</b>
- Outlier Low-High: <b>{lh} desa</b>
- Tidak Signifikan: <b>{ns} desa</b>

<b>4. Hotspot Analysis (Getis-Ord Gi*):</b>
- Hotspot signifikan: <b>{n_hot} desa</b>
- Coldspot signifikan: <b>{n_cold} desa</b>
- Tidak signifikan: <b>{n_ns} desa</b>
</div>
""", unsafe_allow_html=True)

# Strategic Recommendations
if n_hot > 0:
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%); padding: 2rem; border-radius: 1.5rem; border-left: 8px solid #cb181d; box-shadow: 0 8px 24px rgba(0,0,0,0.12); margin: 1.5rem 0;">
<h4 style="color: #cb181d; margin-top: 0;">🎯 PRIORITAS UTAMA INTERVENSI</h4>

<b>Terdapat {n_hot} desa hotspot yang membutuhkan intervensi segera.</b>

<b>Strategi Intervensi Terpadu:</b>

<b>A. Intervensi Jangka Pendek (0-6 bulan):</b>
1. <b>Screening Massal:</b> Lakukan screening stunting menyeluruh di {n_hot} desa hotspot
2. <b>Pemberian PMT:</b> Distribusi Pemberian Makanan Tambahan untuk balita stunting
3. <b>Edukasi Gizi:</b> Program penyuluhan gizi intensif untuk ibu dan keluarga
4. <b>Monitoring Ketat:</b> Pemantauan pertumbuhan bulanan dengan posyandu mobile

<b>B. Intervensi Jangka Menengah (6-12 bulan):</b>
1. <b>Pemberdayaan Kader:</b> Training kader kesehatan di desa hotspot
2. <b>Program Kebun Gizi:</b> Inisiasi kebun keluarga untuk diversifikasi pangan
3. <b>Akses Air Bersih:</b> Perbaikan sanitasi dan akses air bersih
4. <b>Ekonomi Keluarga:</b> Program pemberdayaan ekonomi keluarga miskin

<b>C. Intervensi Jangka Panjang (1-3 tahun):</b>
1. <b>Sistem Surveilans:</b> Bangun sistem early warning stunting berbasis data
2. <b>Kolaborasi Multi-sektor:</b> Kerjasama Dinkes, Dinas Sosial, BKKBN
3. <b>Policy Advocacy:</b> Usulan kebijakan desa peduli stunting
4. <b>Sustainability:</b> Program berkelanjutan berbasis masyarakat
</div>
""", unsafe_allow_html=True)

if ll > 0:
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 2rem; border-radius: 1.5rem; border-left: 8px solid #2171b5; box-shadow: 0 8px 24px rgba(0,0,0,0.12); margin: 1.5rem 0;">
<h4 style="color: #2171b5; margin-top: 0;">✨ PEMBELAJARAN DARI BEST PRACTICE</h4>

<b>{ll} desa coldspot menunjukkan keberhasilan dalam penanganan stunting.</b>

<b>Langkah-langkah Pembelajaran:</b>

1. <b>Dokumentasi Best Practice:</b> Identifikasi dan dokumentasikan program yang berhasil
2. <b>Faktor Keberhasilan:</b> Analisis mengapa desa ini berhasil menekan stunting
3. <b>Knowledge Transfer:</b> Selenggarakan workshop antar desa
4. <b>Mentor Program:</b> Jadikan coldspot sebagai mentor bagi hotspot
5. <b>Replikasi Model:</b> Adaptasi dan terapkan model sukses ke desa lain
</div>
""", unsafe_allow_html=True)

# Final Conclusion
st.markdown(f"""
<div style="background: white; padding: 2.5rem; border-radius: 1.5rem; box-shadow: 0 12px 35px rgba(0,0,0,0.15); margin: 2rem 0; border-top: 6px solid #667eea;">
<h4 style="color: #667eea; margin-top: 0; font-size: 1.6rem;">💡 Kesimpulan Akhir</h4>

<p style="font-size: 1.1rem; line-height: 1.8;">
{"<b>Analisis geospasial menunjukkan adanya pola clustering stunting yang signifikan</b> di Kabupaten Sidoarjo. " if moran.p_sim < 0.05 else "<b>Secara global, pola stunting tidak menunjukkan clustering yang kuat</b>, namun analisis lokal mengidentifikasi area-area spesifik yang memerlukan perhatian. "}
Terdapat <b>{n_hot} desa hotspot</b> yang harus menjadi <b>prioritas utama intervensi</b>.
</p>

<p style="font-size: 1.1rem; line-height: 1.8;">
Pendekatan <b>berbasis area (area-based approach)</b> dengan fokus pada cluster hotspot 
akan lebih efektif dan efisien dibandingkan intervensi merata ke seluruh wilayah. 
Kolaborasi lintas sektor dan pembelajaran dari desa coldspot menjadi kunci keberhasilan 
program percepatan penurunan stunting.
</p>

<p style="font-size: 1.1rem; line-height: 1.8; margin-bottom: 0;">
<b>Rekomendasi utama:</b> Alokasikan <b>60-70% sumber daya</b> ke {n_hot} desa hotspot, 
<b>20-30% untuk monitoring</b> desa lainnya, dan <b>10% untuk dokumentasi best practice</b> 
dari desa coldspot.
</p>
</div>
""", unsafe_allow_html=True)

# Spatial Islands Warning
if islands:
    st.markdown(f"""
<div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); padding: 1.5rem; border-radius: 1rem; border-left: 6px solid #ffa726; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 1.5rem;">
<b>⚠️ Catatan Teknis:</b><br>
Terdapat <b>{len(islands)} desa</b> yang tidak memiliki tetangga geografis langsung (spatial islands) 
sehingga tidak diikutsertakan dalam analisis spasial. Desa-desa ini tetap perlu dimonitor 
secara individual meskipun tidak dapat dianalisis secara spasial.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: white; font-size: 0.95rem;">
    <p style="margin: 0;"><b>📊 Analisis Geospasial Stunting Kabupaten Sidoarjo</b></p>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        Menggunakan metode: Moran's I, LISA, dan Getis-Ord Gi* | 
        Data tingkat desa dengan spatial weights Queen contiguity
    </p>
</div>
""", unsafe_allow_html=True)