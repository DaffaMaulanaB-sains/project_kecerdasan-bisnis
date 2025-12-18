# pages/3_Analisis_Mendalam.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Analisis Stunting", page_icon="📈", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data_skrinning_stunting(1).csv')
        df['tgl_pengambilan_data'] = pd.to_datetime(df['tgl_pengambilan_data'], format='%m/%d/%Y', errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_data()

if df is not None:
    st.title("📈 Analisis Mendalam Status Stunting")
    
    # Sidebar
    st.sidebar.header("⚙️ Pengaturan Analisis")
    
    analysis_type = st.sidebar.selectbox(
        "Pilih Jenis Analisis",
        ["Z-Score Analysis", "Status Gizi", "Perbandingan Puskesmas", "Tren Temporal"]
    )
    
    # Filters
    kecamatan_list = ['Semua'] + sorted(df['nama_kecamatan'].dropna().unique().tolist())
    selected_kecamatan = st.sidebar.selectbox("Kecamatan", kecamatan_list)
    
    filtered_df = df.copy()
    if selected_kecamatan != 'Semua':
        filtered_df = filtered_df[filtered_df['nama_kecamatan'] == selected_kecamatan]
    
    # Analysis sections
    if analysis_type == "Z-Score Analysis":
        st.markdown("### 📊 Analisis Z-Score")
        st.info("""
        Z-Score mengukur seberapa jauh nilai individu dari rata-rata populasi.
        - **Z-Score < -2**: Menunjukkan status gizi kurang atau stunting
        - **Z-Score -2 s/d +2**: Normal
        - **Z-Score > +2**: Di atas normal
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Z-Score TB/U vs BB/TB
            fig_scatter = px.scatter(
                filtered_df,
                x='zsc_tbu',
                y='zsc_bbtb',
                color='stunting_balita',
                size='bb_balita',
                hover_data=['nama_balita', 'umur_balita', 'jenis_kelamin_balita', 'nama_kecamatan'],
                title="Z-Score TB/U vs BB/TB",
                labels={
                    'zsc_tbu': 'Z-Score TB/U (Tinggi/Umur)',
                    'zsc_bbtb': 'Z-Score BB/TB (Berat/Tinggi)'
                },
                color_discrete_map={'Ya': '#e74c3c', 'Tidak': '#2ecc71'}
            )
            fig_scatter.add_hline(y=-2, line_dash="dash", line_color="red", 
                                 annotation_text="Batas Gizi Kurang", annotation_position="right")
            fig_scatter.add_vline(x=-2, line_dash="dash", line_color="red", 
                                 annotation_text="Batas Stunting", annotation_position="top")
            fig_scatter.add_hline(y=-3, line_dash="dot", line_color="darkred", 
                                 annotation_text="Gizi Buruk")
            fig_scatter.add_vline(x=-3, line_dash="dot", line_color="darkred", 
                                 annotation_text="Sangat Pendek")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Z-Score TB/U vs BB/U
            fig_scatter2 = px.scatter(
                filtered_df,
                x='zsc_tbu',
                y='zsc_bbu',
                color='jenis_kelamin_balita',
                size='tb_balita',
                hover_data=['nama_balita', 'umur_balita', 'stunting_balita', 'nama_kecamatan'],
                title="Z-Score TB/U vs BB/U",
                labels={
                    'zsc_tbu': 'Z-Score TB/U',
                    'zsc_bbu': 'Z-Score BB/U'
                },
                color_discrete_map={'Laki - Laki': '#3498db', 'Perempuan': '#e91e63'}
            )
            fig_scatter2.add_hline(y=-2, line_dash="dash", line_color="red")
            fig_scatter2.add_vline(x=-2, line_dash="dash", line_color="red")
            st.plotly_chart(fig_scatter2, use_container_width=True)
        
        # Distribution of Z-Scores
        st.markdown("#### Distribusi Z-Score")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            fig_hist_tbu = px.histogram(
                filtered_df,
                x='zsc_tbu',
                nbins=30,
                title="Distribusi Z-Score TB/U",
                labels={'zsc_tbu': 'Z-Score TB/U'},
                color_discrete_sequence=['#3498db']
            )
            fig_hist_tbu.add_vline(x=-2, line_dash="dash", line_color="red")
            st.plotly_chart(fig_hist_tbu, use_container_width=True)
        
        with col4:
            fig_hist_bbtb = px.histogram(
                filtered_df,
                x='zsc_bbtb',
                nbins=30,
                title="Distribusi Z-Score BB/TB",
                labels={'zsc_bbtb': 'Z-Score BB/TB'},
                color_discrete_sequence=['#2ecc71']
            )
            fig_hist_bbtb.add_vline(x=-2, line_dash="dash", line_color="red")
            st.plotly_chart(fig_hist_bbtb, use_container_width=True)
        
        with col5:
            fig_hist_bbu = px.histogram(
                filtered_df,
                x='zsc_bbu',
                nbins=30,
                title="Distribusi Z-Score BB/U",
                labels={'zsc_bbu': 'Z-Score BB/U'},
                color_discrete_sequence=['#f39c12']
            )
            fig_hist_bbu.add_vline(x=-2, line_dash="dash", line_color="red")
            st.plotly_chart(fig_hist_bbu, use_container_width=True)
    
    elif analysis_type == "Status Gizi":
        st.markdown("### 🍽️ Analisis Status Gizi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Status TB/U
            status_tbu = filtered_df['status_tbu'].value_counts()
            fig_tbu = px.pie(
                values=status_tbu.values,
                names=status_tbu.index,
                title="Status TB/U (Tinggi Badan/Umur)",
                hole=0.4
            )
            st.plotly_chart(fig_tbu, use_container_width=True)
            
            st.metric("Total Pendek + Sangat Pendek", 
                     len(filtered_df[filtered_df['status_tbu'].isin(['Pendek', 'Sangat Pendek'])]))
        
        with col2:
            # Status BB/TB
            status_bbtb = filtered_df['status_bbtb'].value_counts()
            fig_bbtb = px.pie(
                values=status_bbtb.values,
                names=status_bbtb.index,
                title="Status BB/TB (Berat/Tinggi)",
                hole=0.4
            )
            st.plotly_chart(fig_bbtb, use_container_width=True)
            
            st.metric("Total Gizi Kurang + Buruk", 
                     len(filtered_df[filtered_df['status_bbtb'].str.contains('Kurang|Buruk', na=False)]))
        
        with col3:
            # Status BB/U
            status_bbu = filtered_df['status_bbu'].value_counts()
            fig_bbu = px.pie(
                values=status_bbu.values,
                names=status_bbu.index,
                title="Status BB/U (Berat Badan/Umur)",
                hole=0.4
            )
            st.plotly_chart(fig_bbu, use_container_width=True)
            
            st.metric("Total BB Kurang + Sangat Kurang", 
                     len(filtered_df[filtered_df['status_bbu'].str.contains('Kurang', na=False)]))
        
        # Crosstab analysis
        st.markdown("#### Hubungan Status TB/U dan BB/TB")
        crosstab = pd.crosstab(filtered_df['status_tbu'], filtered_df['status_bbtb'])
        
        fig_heatmap = px.imshow(
            crosstab,
            labels=dict(x="Status BB/TB", y="Status TB/U", color="Jumlah"),
            title="Heatmap Hubungan Status TB/U dan BB/TB",
            color_continuous_scale='Reds',
            text_auto=True
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif analysis_type == "Perbandingan Puskesmas":
        st.markdown("### 🏥 Perbandingan Antar Puskesmas")
        
        # Agregat data per puskesmas
        pusk_stats = filtered_df.groupby('nama_puskesmas').agg({
            'nama_balita': 'count',
            'stunting_balita': lambda x: (x == 'Ya').sum(),
            'zsc_tbu': 'mean',
            'zsc_bbtb': 'mean',
            'zsc_bbu': 'mean'
        }).reset_index()
        
        pusk_stats.columns = ['Puskesmas', 'Total Balita', 'Jumlah Stunting', 
                              'Rata-rata Z-Score TB/U', 'Rata-rata Z-Score BB/TB', 'Rata-rata Z-Score BB/U']
        pusk_stats['Persentase Stunting (%)'] = (pusk_stats['Jumlah Stunting'] / pusk_stats['Total Balita'] * 100).round(2)
        pusk_stats = pusk_stats.sort_values('Persentase Stunting (%)', ascending=False)
        
        # Bar chart persentase
        fig_pusk_pct = px.bar(
            pusk_stats,
            x='Puskesmas',
            y='Persentase Stunting (%)',
            color='Persentase Stunting (%)',
            title="Persentase Stunting per Puskesmas",
            color_continuous_scale='Reds',
            text='Persentase Stunting (%)'
        )
        fig_pusk_pct.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_pusk_pct.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pusk_pct, use_container_width=True)
        
        # Comparison table
        st.markdown("#### Tabel Perbandingan Detail")
        st.dataframe(pusk_stats.style.background_gradient(subset=['Persentase Stunting (%)'], cmap='Reds'), 
                    use_container_width=True)
        
        # Z-Score comparison
        st.markdown("#### Perbandingan Rata-rata Z-Score")
        
        fig_zscore_compare = go.Figure()
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score TB/U'],
            name='TB/U',
            marker_color='#3498db'
        ))
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score BB/TB'],
            name='BB/TB',
            marker_color='#2ecc71'
        ))
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score BB/U'],
            name='BB/U',
            marker_color='#f39c12'
        ))
        fig_zscore_compare.add_hline(y=-2, line_dash="dash", line_color="red", 
                                     annotation_text="Batas Normal")
        fig_zscore_compare.update_layout(
            title="Rata-rata Z-Score per Puskesmas",
            xaxis_tickangle=-45,
            barmode='group'
        )
        st.plotly_chart(fig_zscore_compare, use_container_width=True)
    
    else:  # Tren Temporal
        st.markdown("### 📅 Analisis Tren Temporal")
        
        # Group by date
        temporal_data = filtered_df.groupby(filtered_df['tgl_pengambilan_data'].dt.to_period('M')).agg({
            'nama_balita': 'count',
            'stunting_balita': lambda x: (x == 'Ya').sum()
        }).reset_index()
        
        temporal_data['tgl_pengambilan_data'] = temporal_data['tgl_pengambilan_data'].dt.to_timestamp()
        temporal_data.columns = ['Bulan', 'Total Balita', 'Jumlah Stunting']
        temporal_data['Persentase Stunting'] = (temporal_data['Jumlah Stunting'] / temporal_data['Total Balita'] * 100).round(2)
        
        # Line chart
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=temporal_data['Bulan'],
            y=temporal_data['Jumlah Stunting'],
            mode='lines+markers',
            name='Jumlah Stunting',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10)
        ))
        fig_trend.add_trace(go.Scatter(
            x=temporal_data['Bulan'],
            y=temporal_data['Persentase Stunting'],
            mode='lines+markers',
            name='Persentase (%)',
            yaxis='y2',
            line=dict(color='#3498db', width=3, dash='dash'),
            marker=dict(size=10)
        ))
        fig_trend.update_layout(
            title='Tren Kasus Stunting dari Waktu ke Waktu',
            xaxis_title='Bulan',
            yaxis_title='Jumlah Kasus',
            yaxis2=dict(
                title='Persentase (%)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Data table
        st.markdown("#### Data Temporal")
        st.dataframe(temporal_data, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rata-rata Kasus/Bulan", f"{temporal_data['Jumlah Stunting'].mean():.1f}")
        with col2:
            st.metric("Bulan dengan Kasus Tertinggi", 
                     temporal_data.loc[temporal_data['Jumlah Stunting'].idxmax(), 'Bulan'].strftime('%B %Y'))
        with col3:
            st.metric("Total Kasus", f"{temporal_data['Jumlah Stunting'].sum():,}")

else:
    st.error("❌ Data tidak dapat dimuat.")