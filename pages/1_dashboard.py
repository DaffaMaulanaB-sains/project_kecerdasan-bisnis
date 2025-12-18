# pages/1_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Stunting", page_icon="📊", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data_skrinning_stunting(1).csv')
        df['tgl_pengambilan_data'] = pd.to_datetime(df['tgl_pengambilan_data'], format='%m/%d/%Y', errors='coerce')
        df['tgl_lahir_balita'] = pd.to_datetime(df['tgl_lahir_balita'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    st.title("📊 Dashboard Stunting Sidoarjo")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    
    kecamatan_list = ['Semua'] + sorted(df['nama_kecamatan'].dropna().unique().tolist())
    selected_kecamatan = st.sidebar.selectbox("Pilih Kecamatan", kecamatan_list)
    
    if selected_kecamatan != 'Semua':
        puskesmas_list = ['Semua'] + sorted(df[df['nama_kecamatan'] == selected_kecamatan]['nama_puskesmas'].dropna().unique().tolist())
    else:
        puskesmas_list = ['Semua'] + sorted(df['nama_puskesmas'].dropna().unique().tolist())
    selected_puskesmas = st.sidebar.selectbox("Pilih Puskesmas", puskesmas_list)
    
    gender_filter = st.sidebar.multiselect(
        "Jenis Kelamin",
        options=df['jenis_kelamin_balita'].unique().tolist(),
        default=df['jenis_kelamin_balita'].unique().tolist()
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_kecamatan != 'Semua':
        filtered_df = filtered_df[filtered_df['nama_kecamatan'] == selected_kecamatan]
    if selected_puskesmas != 'Semua':
        filtered_df = filtered_df[filtered_df['nama_puskesmas'] == selected_puskesmas]
    if gender_filter:
        filtered_df = filtered_df[filtered_df['jenis_kelamin_balita'].isin(gender_filter)]
    
    # KPI Metrics
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_balita = len(filtered_df)
    stunting_count = len(filtered_df[filtered_df['stunting_balita'] == 'Ya'])
    stunting_rate = (stunting_count / total_balita * 100) if total_balita > 0 else 0
    
    with col1:
        st.metric("Total Balita", f"{total_balita:,}")
    with col2:
        st.metric("Kasus Stunting", f"{stunting_count:,}", delta=f"-{stunting_rate:.1f}%", delta_color="inverse")
    with col3:
        st.metric("Normal", f"{total_balita - stunting_count:,}")
    with col4:
        laki = len(filtered_df[filtered_df['jenis_kelamin_balita'] == 'Laki - Laki'])
        st.metric("👦 Laki-laki", f"{laki:,}")
    with col5:
        perempuan = len(filtered_df[filtered_df['jenis_kelamin_balita'] == 'Perempuan'])
        st.metric("👧 Perempuan", f"{perempuan:,}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart status stunting
        stunting_counts = filtered_df['stunting_balita'].value_counts()
        colors = ['#2ecc71', '#e74c3c'] if 'Tidak' in stunting_counts.index else ['#e74c3c']
        fig_pie = px.pie(
            values=stunting_counts.values,
            names=stunting_counts.index,
            title="Status Stunting",
            color_discrete_sequence=colors,
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart by gender
        gender_data = filtered_df.groupby(['jenis_kelamin_balita', 'stunting_balita']).size().reset_index(name='count')
        fig_gender = px.bar(
            gender_data,
            x='jenis_kelamin_balita',
            y='count',
            color='stunting_balita',
            title="Status Stunting Berdasarkan Jenis Kelamin",
            labels={'count': 'Jumlah', 'jenis_kelamin_balita': 'Jenis Kelamin'},
            barmode='group',
            color_discrete_map={'Ya': '#e74c3c', 'Tidak': '#2ecc71'}
        )
        st.plotly_chart(fig_gender, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Stunting by kecamatan
        kec_data = filtered_df.groupby(['nama_kecamatan', 'stunting_balita']).size().reset_index(name='count')
        kec_pivot = kec_data.pivot(index='nama_kecamatan', columns='stunting_balita', values='count').fillna(0)
        kec_pivot['Total'] = kec_pivot.sum(axis=1)
        kec_pivot = kec_pivot.sort_values('Total', ascending=True)
        
        fig_kec = go.Figure()
        if 'Ya' in kec_pivot.columns:
            fig_kec.add_trace(go.Bar(
                y=kec_pivot.index,
                x=kec_pivot['Ya'],
                name='Stunting',
                orientation='h',
                marker_color='#e74c3c'
            ))
        if 'Tidak' in kec_pivot.columns:
            fig_kec.add_trace(go.Bar(
                y=kec_pivot.index,
                x=kec_pivot['Tidak'],
                name='Normal',
                orientation='h',
                marker_color='#2ecc71'
            ))
        fig_kec.update_layout(
            title="Distribusi Stunting per Kecamatan",
            barmode='stack',
            xaxis_title="Jumlah",
            yaxis_title="Kecamatan"
        )
        st.plotly_chart(fig_kec, use_container_width=True)
    
    with col4:
        # Status TB/U distribution
        status_tbu = filtered_df['status_tbu'].value_counts()
        fig_tbu = px.bar(
            x=status_tbu.values,
            y=status_tbu.index,
            orientation='h',
            title="Distribusi Status TB/U (Tinggi Badan/Umur)",
            labels={'x': 'Jumlah', 'y': 'Status TB/U'},
            color=status_tbu.values,
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_tbu, use_container_width=True)
    
    # Status Gizi
    st.markdown("### 🍽️ Status Gizi")
    col5, col6 = st.columns(2)
    
    with col5:
        status_bbtb = filtered_df['status_bbtb'].value_counts()
        fig_bbtb = px.pie(
            values=status_bbtb.values,
            names=status_bbtb.index,
            title="Status BB/TB (Berat Badan/Tinggi Badan)",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_bbtb, use_container_width=True)
    
    with col6:
        status_bbu = filtered_df['status_bbu'].value_counts()
        fig_bbu = px.pie(
            values=status_bbu.values,
            names=status_bbu.index,
            title="Status BB/U (Berat Badan/Umur)",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_bbu, use_container_width=True)
    
    # Top 5 Puskesmas dengan kasus tertinggi
    st.markdown("### 🏥 Top 5 Puskesmas dengan Kasus Stunting Tertinggi")
    pusk_stunting = filtered_df[filtered_df['stunting_balita'] == 'Ya'].groupby('nama_puskesmas').size().sort_values(ascending=False).head(5)
    
    fig_top_pusk = px.bar(
        x=pusk_stunting.values,
        y=pusk_stunting.index,
        orientation='h',
        labels={'x': 'Jumlah Kasus', 'y': 'Puskesmas'},
        color=pusk_stunting.values,
        color_continuous_scale='Reds'
    )
    fig_top_pusk.update_layout(showlegend=False)
    st.plotly_chart(fig_top_pusk, use_container_width=True)
    
else:
    st.error("❌ Data tidak dapat dimuat. Pastikan file 'data_skrinning_stunting(1).csv' tersedia.")