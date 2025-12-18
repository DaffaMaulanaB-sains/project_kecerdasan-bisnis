# pages/2_Peta_Sebaran.py
# ==========================================================
# DASHBOARD PETA SEBARAN STUNTING KABUPATEN SIDOARJO
# Gabungan Code 1 (Design Modern) + Code 2 (Logika Robust)
# - Tidak error walau peta desa TIDAK ADA
# - Mode desa otomatis nonaktif jika file tidak ditemukan
# - Design modern dengan CSS styling
# ==========================================================

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json
from pathlib import Path

st.set_page_config(page_title="Peta Sebaran Stunting", page_icon="🗺️", layout="wide")

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .top-kecamatan-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-left: 6px solid;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .top-kecamatan-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    .rank-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .kecamatan-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0.5rem 0;
        letter-spacing: 0.5px;
    }
    
    .percentage {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .count-info {
        color: #718096;
        font-size: 1rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    .rank-1 { border-left-color: #c0392b; background: linear-gradient(135deg, #ffeaea 0%, #ffe0e0 100%); }
    .rank-2 { border-left-color: #e74c3c; background: linear-gradient(135deg, #fff5f5 0%, #ffebeb 100%); }
    .rank-3 { border-left-color: #f39c12; background: linear-gradient(135deg, #fff9f0 0%, #fff3e0 100%); }
    .rank-4 { border-left-color: #f1c40f; background: linear-gradient(135deg, #fffef0 0%, #fffacd 100%); }
    .rank-5 { border-left-color: #e67e22; background: linear-gradient(135deg, #fff8f0 0%, #ffe4d4 100%); }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-top: 4px solid #667eea;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #718096;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .emoji-large {
        font-size: 3rem;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #0284c7;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .info-box-text {
        color: #0c4a6e;
        font-weight: 600;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .legend-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .legend-item:hover {
        background: #f7fafc;
        transform: translateX(5px);
    }
    
    .legend-color {
        width: 40px;
        height: 40px;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .legend-text {
        font-weight: 600;
        color: #2d3748;
    }
</style>
""", unsafe_allow_html=True)

# ===================== PATH CONFIGURATION =====================
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "data_skrinning_stunting(1).csv"
KEC_GEOJSON = DATA_DIR / "peta_sidoarjo.geojson"
DESA_GEOJSON = DATA_DIR / "peta_sidoarjo_desa.geojson"

# ===================== LOAD DATA FUNCTIONS =====================
@st.cache_data
def load_csv():
    try:
        return pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

@st.cache_data
def load_geojson_kecamatan():
    try:
        return gpd.read_file(KEC_GEOJSON)
    except Exception as e:
        st.error(f"Error loading GeoJSON Kecamatan: {e}")
        return None

@st.cache_data
def load_geojson_desa():
    if DESA_GEOJSON.exists():
        try:
            return gpd.read_file(DESA_GEOJSON)
        except Exception as e:
            return None
    return None

# ===================== INITIALIZE DATA =====================
df = load_csv()
gdf_kecamatan = load_geojson_kecamatan()
gdf_desa = load_geojson_desa()

# Check if desa mode is available
DESA_MODE_AVAILABLE = gdf_desa is not None

if df is None or gdf_kecamatan is None:
    st.error("❌ Data tidak dapat dimuat. Pastikan file CSV dan GeoJSON tersedia.")
    st.stop()

# ===================== HEADER =====================
st.markdown("""
<div class="main-header">
    <h1>🗺️ Peta Prevalensi Stunting Kabupaten Sidoarjo</h1>
    <p style="font-size: 1.1rem; margin-top: 0.5rem; opacity: 0.9;">
        Dashboard Interaktif Pemantauan & Analisis Data Stunting
    </p>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; margin-bottom: 1.5rem;">
    <h2 style="color: white; margin: 0; font-size: 1.5rem;">🎯 Panel Filter</h2>
</div>
""", unsafe_allow_html=True)

# View Mode Selection
st.sidebar.markdown("### 🔍 Mode Tampilan")
view_options = ["📍 Seluruh Sidoarjo", "🏘️ Per Kecamatan"]
if DESA_MODE_AVAILABLE:
    view_options.append("🏠 Per Desa")

view_mode = st.sidebar.radio("Pilih tingkat detail:", view_options)

# Conditional Filters
selected_kecamatan = None
selected_desa = None

if view_mode in ["🏘️ Per Kecamatan", "🏠 Per Desa"]:
    st.sidebar.markdown("### 🏘️ Pilih Kecamatan")
    kecamatan_list = ['Semua'] + sorted(df['nama_kecamatan'].dropna().unique().tolist())
    selected_kecamatan = st.sidebar.selectbox("Kecamatan:", kecamatan_list)

if view_mode == "🏠 Per Desa" and selected_kecamatan and selected_kecamatan != 'Semua':
    st.sidebar.markdown("### 🏠 Pilih Desa")
    desa_list = sorted(
        df[df['nama_kecamatan'] == selected_kecamatan]['nama_desa']
        .dropna().unique().tolist()
    )
    if desa_list:
        selected_desa = st.sidebar.selectbox("Desa/Kelurahan:", ['Semua Desa'] + desa_list)
    else:
        st.sidebar.warning("⚠️ Tidak ada data desa untuk kecamatan ini")

st.sidebar.markdown("---")

# Other Filters
st.sidebar.markdown("### 🏥 Filter Puskesmas")
puskesmas_list = ['Semua'] + sorted(df['nama_puskesmas'].dropna().unique().tolist())
selected_puskesmas = st.sidebar.selectbox("Puskesmas:", puskesmas_list)

st.sidebar.markdown("### 👶 Jenis Kelamin")
gender_options = st.sidebar.multiselect(
    "Pilih:",
    options=df['jenis_kelamin_balita'].unique().tolist(),
    default=df['jenis_kelamin_balita'].unique().tolist()
)

# ===================== APPLY FILTERS =====================
filtered_df = df.copy()

if selected_puskesmas != 'Semua':
    filtered_df = filtered_df[filtered_df['nama_puskesmas'] == selected_puskesmas]

if gender_options:
    filtered_df = filtered_df[filtered_df['jenis_kelamin_balita'].isin(gender_options)]

if view_mode in ["🏘️ Per Kecamatan", "🏠 Per Desa"] and selected_kecamatan and selected_kecamatan != 'Semua':
    filtered_df = filtered_df[filtered_df['nama_kecamatan'] == selected_kecamatan]

if view_mode == "🏠 Per Desa" and selected_desa and selected_desa != 'Semua Desa':
    filtered_df = filtered_df[filtered_df['nama_desa'] == selected_desa]

# ===================== DETERMINE GROUP & GDF =====================
if view_mode == "🏠 Per Desa" and DESA_MODE_AVAILABLE:
    group_col = 'nama_desa'
    gdf_active = gdf_desa
    geo_candidates = ['nama_desa', 'DESA', 'KELURAHAN', 'NAMOBJ', 'DESA_KELUR', 'WADMKD']
    display_name = 'Desa/Kelurahan'
else:
    group_col = 'nama_kecamatan'
    gdf_active = gdf_kecamatan
    geo_candidates = ['nama_kecamatan', 'KECAMATAN', 'WADMKC', 'NAMOBJ']
    display_name = 'Kecamatan'

# ===================== INFO BOX =====================
view_info_text = "Menampilkan data seluruh Kabupaten Sidoarjo"
if view_mode == "🏘️ Per Kecamatan":
    if selected_kecamatan == 'Semua':
        view_info_text = "Menampilkan data seluruh kecamatan di Kabupaten Sidoarjo"
    else:
        view_info_text = f"Menampilkan data untuk Kecamatan <strong>{selected_kecamatan}</strong>"
elif view_mode == "🏠 Per Desa":
    if not selected_kecamatan or selected_kecamatan == 'Semua':
        view_info_text = "Menampilkan data seluruh desa di Kabupaten Sidoarjo"
    elif selected_desa and selected_desa != 'Semua Desa':
        view_info_text = f"Menampilkan data untuk Desa <strong>{selected_desa}</strong>, Kecamatan <strong>{selected_kecamatan}</strong>"
    else:
        view_info_text = f"Menampilkan seluruh desa di Kecamatan <strong>{selected_kecamatan}</strong>"

st.markdown(f"""
<div class="info-box">
    <div class="info-box-text">
        📍 {view_info_text}
    </div>
</div>
""", unsafe_allow_html=True)

# ===================== AGGREGATE DATA =====================
stunting_data = (
    filtered_df[filtered_df['stunting_balita'] == 'Ya']
    .groupby(group_col)
    .size()
    .reset_index(name='jumlah_stunting')
)

total_data = (
    filtered_df.groupby(group_col)
    .size()
    .reset_index(name='total_balita')
)

map_data = total_data.merge(stunting_data, on=group_col, how='left').fillna(0)
map_data['prevalensi'] = (map_data['jumlah_stunting'] / map_data['total_balita'] * 100).round(2)
map_data = map_data.sort_values('prevalensi', ascending=False)

# ===================== METRICS =====================
col1, col2, col3, col4 = st.columns(4)

total_balita = int(map_data['total_balita'].sum())
total_stunting = int(map_data['jumlah_stunting'].sum())
avg_prevalensi = map_data['prevalensi'].mean() if len(map_data) > 0 else 0
jumlah_wilayah = len(map_data)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="emoji-large">👶</div>
        <div class="metric-value">{total_balita:,}</div>
        <div class="metric-label">Total Balita</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-top-color: #e74c3c;">
        <div class="emoji-large">⚠️</div>
        <div class="metric-value" style="color: #e74c3c;">{total_stunting:,}</div>
        <div class="metric-label">Kasus Stunting</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-top-color: #f39c12;">
        <div class="emoji-large">📊</div>
        <div class="metric-value" style="color: #f39c12;">{avg_prevalensi:.2f}%</div>
        <div class="metric-label">Rata-rata Prevalensi</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-top-color: #2ecc71;">
        <div class="emoji-large">📍</div>
        <div class="metric-value" style="color: #2ecc71;">{jumlah_wilayah}</div>
        <div class="metric-label">Jumlah {display_name}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===================== MERGE WITH GEODATAFRAME =====================
name_col = None
for c in geo_candidates:
    if c in gdf_active.columns:
        name_col = c
        break

if name_col is None:
    st.error(f"❌ Kolom nama wilayah tidak ditemukan pada GeoJSON. Tersedia: {list(gdf_active.columns)}")
    st.stop()

# Normalize names for matching
gdf_active[name_col] = gdf_active[name_col].astype(str).str.strip().str.lower()
map_data[group_col] = map_data[group_col].astype(str).str.strip().str.lower()

gdf_map = gdf_active.merge(
    map_data,
    left_on=name_col,
    right_on=group_col,
    how='left'
).fillna(0)

gdf_map = gdf_map.to_crs(epsg=4326)

# ===================== LAYOUT: MAP + RANKING =====================
col_map, col_rank = st.columns([2, 1])

with col_map:
    st.markdown('<div class="section-header">🗺️ Peta Interaktif</div>', unsafe_allow_html=True)
    
    # Calculate map center
    bounds = gdf_map.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    
    # Determine zoom based on view mode
    if view_mode == "🏠 Per Desa" and selected_desa and selected_desa != 'Semua Desa':
        zoom_level = 13
    elif view_mode in ["🏘️ Per Kecamatan", "🏠 Per Desa"] and selected_kecamatan and selected_kecamatan != 'Semua':
        zoom_level = 11
    else:
        zoom_level = 10
    
    # Create map
    fig = px.choropleth_mapbox(
        gdf_map,
        geojson=json.loads(gdf_map.to_json()),
        locations=gdf_map.index,
        color='prevalensi',
        hover_name=name_col,
        hover_data={
            'jumlah_stunting': ':,.0f',
            'total_balita': ':,.0f',
            'prevalensi': ':.2f'
        },
        color_continuous_scale='YlOrRd',
        mapbox_style='carto-positron',
        zoom=zoom_level,
        center={'lat': center_lat, 'lon': center_lon},
        opacity=0.85,
        labels={
            'prevalensi': 'Prevalensi (%)',
            'jumlah_stunting': 'Kasus Stunting',
            'total_balita': 'Total Balita'
        }
    )
    
    fig.update_traces(marker_line_width=1.5, marker_line_color='white')
    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(
                text="Prevalensi<br>Stunting (%)",
                font=dict(size=14, family="Inter", weight="bold")
            ),
            thickness=22,
            len=0.7,
            x=0.02,
            xanchor="left",
            tickfont=dict(size=12)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_rank:
    st.markdown(f'<div class="section-header">⚠️ Top 5 {display_name}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color: #718096; font-weight: 600; margin-bottom: 1rem;'>Berdasarkan Prevalensi Tertinggi</p>", unsafe_allow_html=True)
    
    top_5 = map_data.head(5)
    rank_classes = ['rank-1', 'rank-2', 'rank-3', 'rank-4', 'rank-5']
    rank_emojis = ['🔴', '🟠', '🟡', '🟢', '🔵']
    
    if len(top_5) == 0:
        st.warning("⚠️ Tidak ada data untuk ditampilkan")
    else:
        for idx, (_, row) in enumerate(top_5.iterrows()):
            rank = idx + 1
            rank_class = rank_classes[idx] if idx < len(rank_classes) else 'rank-5'
            rank_emoji = rank_emojis[idx] if idx < len(rank_emojis) else '🔴'
            
            area_name = row[group_col]
            
            st.markdown(f"""
            <div class="top-kecamatan-card {rank_class}">
                <div class="rank-badge">#{rank}</div>
                <div style="display: flex; align-items: center; gap: 1.5rem; padding-right: 3rem;">
                    <span class="emoji-large">{rank_emoji}</span>
                    <div style="flex: 1;">
                        <div class="kecamatan-name">{area_name.upper()}</div>
                        <div class="percentage">{row['prevalensi']:.2f}%</div>
                        <div class="count-info">
                            💉 {int(row['jumlah_stunting'])} dari {int(row['total_balita'])} balita
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===================== DATA TABLE =====================
st.markdown(f'<div class="section-header">📋 Data Lengkap per {display_name}</div>', unsafe_allow_html=True)

def style_prevalensi(val):
    if val >= 50:
        return 'background-color: #e74c3c; color: white; font-weight: bold;'
    elif val >= 30:
        return 'background-color: #f39c12; color: white; font-weight: bold;'
    elif val >= 20:
        return 'background-color: #f1c40f; font-weight: bold;'
    elif val >= 10:
        return 'background-color: #ffeda0; font-weight: bold;'
    else:
        return 'background-color: #2ecc71; color: white; font-weight: bold;'

display_table = map_data.copy()
display_table['Ranking'] = range(1, len(display_table) + 1)
display_table = display_table[['Ranking', group_col, 'jumlah_stunting', 'total_balita', 'prevalensi']]
display_table.columns = ['Ranking', display_name, 'Kasus Stunting', 'Total Balita', 'Prevalensi (%)']

display_table['Kasus Stunting'] = display_table['Kasus Stunting'].astype(int)
display_table['Total Balita'] = display_table['Total Balita'].astype(int)

styled_table = display_table.style.applymap(
    style_prevalensi,
    subset=['Prevalensi (%)']
).format({
    'Kasus Stunting': '{:,}',
    'Total Balita': '{:,}',
    'Prevalensi (%)': '{:.2f}%'
})

st.dataframe(styled_table, use_container_width=True, height=400)

# ===================== LEGEND =====================
st.markdown('<div class="section-header">📌 Kategori Prevalensi Stunting</div>', unsafe_allow_html=True)

legend_html = """
<div class="legend-container">
    <div class="legend-item">
        <div class="legend-color" style="background: #e74c3c;"></div>
        <div class="legend-text">🔴 Sangat Tinggi (≥50%) - Memerlukan intervensi segera</div>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: #f39c12;"></div>
        <div class="legend-text">🟠 Tinggi (30-49%) - Perlu perhatian khusus</div>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: #f1c40f;"></div>
        <div class="legend-text">🟡 Sedang (20-29%) - Monitoring ketat</div>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: #ffeda0;"></div>
        <div class="legend-text">🟢 Rendah (10-19%) - Monitoring rutin</div>
    </div>
    <div class="legend-item">
        <div class="legend-color" style="background: #2ecc71;"></div>
        <div class="legend-text">✅ Sangat Rendah (&lt;10%) - Pertahankan program</div>
    </div>
</div>
"""
st.markdown(legend_html, unsafe_allow_html=True)

# ===================== DOWNLOAD =====================
st.markdown('<div class="section-header">💾 Unduh Data</div>', unsafe_allow_html=True)

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv = display_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name=f"prevalensi_stunting_sidoarjo_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_dl2:
    try:
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            display_table.to_excel(writer, index=False, sheet_name='Data Stunting')
        
        st.download_button(
            label="📊 Download Data Excel",
            data=buffer.getvalue(),
            file_name=f"prevalensi_stunting_sidoarjo_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except ImportError:
        st.info("💡 Install openpyxl untuk download Excel: `pip install openpyxl`")

# ===================== FOOTER =====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem;">
    <p style="font-size: 0.9rem; margin: 0;">
        📊 Dashboard Peta Prevalensi Stunting Kabupaten Sidoarjo
    </p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">
        Data diperbarui secara berkala | Untuk informasi lebih lanjut hubungi Dinas Kesehatan Sidoarjo
    </p>
