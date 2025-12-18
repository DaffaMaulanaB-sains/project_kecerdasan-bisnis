# pages/3_Analisis_Mendalam.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

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
        
        # Info box yang lebih menarik
        st.info("""
        **Z-Score** mengukur seberapa jauh nilai individu dari rata-rata populasi (dalam satuan standar deviasi).
        
        📏 **Interpretasi Z-Score:**
        - **Z < -3**: Sangat Pendek/Sangat Kurang (Severe)
        - **-3 ≤ Z < -2**: Pendek/Kurang (Moderate)
        - **-2 ≤ Z ≤ +2**: Normal
        - **Z > +2**: Tinggi/Lebih (di atas normal)
        """)
        
        # Metrics ringkasan
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        severe_stunting = len(filtered_df[filtered_df['zsc_tbu'] < -3])
        moderate_stunting = len(filtered_df[(filtered_df['zsc_tbu'] >= -3) & (filtered_df['zsc_tbu'] < -2)])
        normal = len(filtered_df[(filtered_df['zsc_tbu'] >= -2) & (filtered_df['zsc_tbu'] <= 2)])
        
        col_m1.metric("🔴 Sangat Pendek", severe_stunting, 
                     delta=f"{(severe_stunting/len(filtered_df)*100):.1f}%", delta_color="inverse")
        col_m2.metric("🟠 Pendek", moderate_stunting,
                     delta=f"{(moderate_stunting/len(filtered_df)*100):.1f}%", delta_color="inverse")
        col_m3.metric("🟢 Normal", normal,
                     delta=f"{(normal/len(filtered_df)*100):.1f}%", delta_color="normal")
        col_m4.metric("📊 Total Sampel", len(filtered_df))
        
        st.markdown("---")
        
        # Scatter plots dengan styling yang lebih baik
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📍 Z-Score TB/U vs BB/TB")
            st.caption("Hubungan antara tinggi badan dan berat badan balita")
            
            fig_scatter = px.scatter(
                filtered_df,
                x='zsc_tbu',
                y='zsc_bbtb',
                color='stunting_balita',
                size='bb_balita',
                hover_data={
                    'nama_balita': True,
                    'umur_balita': True,
                    'jenis_kelamin_balita': True,
                    'nama_kecamatan': True,
                    'zsc_tbu': ':.2f',
                    'zsc_bbtb': ':.2f',
                    'bb_balita': ':.1f'
                },
                labels={
                    'zsc_tbu': 'Z-Score TB/U (Tinggi/Umur)',
                    'zsc_bbtb': 'Z-Score BB/TB (Berat/Tinggi)',
                    'stunting_balita': 'Status Stunting'
                },
                color_discrete_map={'Ya': '#e74c3c', 'Tidak': '#2ecc71'},
                opacity=0.7
            )
            
            # Garis referensi yang lebih jelas
            fig_scatter.add_hline(y=-2, line_dash="dash", line_color="red", line_width=2,
                                 annotation_text="Gizi Kurang", annotation_position="right",
                                 annotation=dict(font_size=12, font_color="red"))
            fig_scatter.add_vline(x=-2, line_dash="dash", line_color="red", line_width=2,
                                 annotation_text="Stunting", annotation_position="top",
                                 annotation=dict(font_size=12, font_color="red"))
            fig_scatter.add_hline(y=-3, line_dash="dot", line_color="darkred", line_width=1.5,
                                 annotation_text="Gizi Buruk", annotation_position="right",
                                 annotation=dict(font_size=10, font_color="darkred"))
            fig_scatter.add_vline(x=-3, line_dash="dot", line_color="darkred", line_width=1.5,
                                 annotation_text="Sangat Pendek", annotation_position="top",
                                 annotation=dict(font_size=10, font_color="darkred"))
            
            # Shaded regions untuk zona bahaya
            fig_scatter.add_shape(type="rect", x0=-6, y0=-6, x1=-2, y1=-2,
                                fillcolor="red", opacity=0.1, layer="below", line_width=0)
            
            fig_scatter.update_layout(
                height=500,
                template="plotly_white",
                hovermode='closest',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            st.markdown("#### 📍 Z-Score TB/U vs BB/U")
            st.caption("Perbandingan tinggi dan berat badan berdasarkan umur")
            
            fig_scatter2 = px.scatter(
                filtered_df,
                x='zsc_tbu',
                y='zsc_bbu',
                color='jenis_kelamin_balita',
                size='tb_balita',
                hover_data={
                    'nama_balita': True,
                    'umur_balita': True,
                    'stunting_balita': True,
                    'nama_kecamatan': True,
                    'zsc_tbu': ':.2f',
                    'zsc_bbu': ':.2f',
                    'tb_balita': ':.1f'
                },
                labels={
                    'zsc_tbu': 'Z-Score TB/U (Tinggi/Umur)',
                    'zsc_bbu': 'Z-Score BB/U (Berat/Umur)',
                    'jenis_kelamin_balita': 'Jenis Kelamin'
                },
                color_discrete_map={'Laki - Laki': '#3498db', 'Perempuan': '#e91e63'},
                opacity=0.7
            )
            
            fig_scatter2.add_hline(y=-2, line_dash="dash", line_color="red", line_width=2,
                                  annotation_text="BB Kurang", annotation_position="right",
                                  annotation=dict(font_size=12, font_color="red"))
            fig_scatter2.add_vline(x=-2, line_dash="dash", line_color="red", line_width=2,
                                  annotation_text="Stunting", annotation_position="top",
                                  annotation=dict(font_size=12, font_color="red"))
            
            fig_scatter2.add_shape(type="rect", x0=-6, y0=-6, x1=-2, y1=-2,
                                 fillcolor="red", opacity=0.1, layer="below", line_width=0)
            
            fig_scatter2.update_layout(
                height=500,
                template="plotly_white",
                hovermode='closest',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_scatter2, use_container_width=True)
        
        st.markdown("---")
        
        # Distribution dengan styling yang lebih baik
        st.markdown("### 📊 Distribusi Z-Score")
        st.caption("Histogram menunjukkan sebaran nilai Z-Score pada populasi balita")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            fig_hist_tbu = go.Figure()
            
            fig_hist_tbu.add_trace(go.Histogram(
                x=filtered_df['zsc_tbu'],
                nbinsx=40,
                marker_color='#3498db',
                opacity=0.75,
                name='TB/U',
                hovertemplate='Z-Score: %{x:.2f}<br>Jumlah: %{y}<extra></extra>'
            ))
            
            fig_hist_tbu.add_vline(x=-2, line_dash="dash", line_color="red", line_width=3,
                                  annotation_text="Batas Stunting", annotation_position="top")
            fig_hist_tbu.add_vline(x=-3, line_dash="dot", line_color="darkred", line_width=2,
                                  annotation_text="Sangat Pendek", annotation_position="bottom")
            fig_hist_tbu.add_vline(x=filtered_df['zsc_tbu'].mean(), line_dash="solid", 
                                  line_color="green", line_width=2,
                                  annotation_text=f"Mean: {filtered_df['zsc_tbu'].mean():.2f}",
                                  annotation_position="top")
            
            fig_hist_tbu.update_layout(
                title="Distribusi Z-Score TB/U",
                xaxis_title="Z-Score TB/U",
                yaxis_title="Frekuensi",
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_hist_tbu, use_container_width=True)
            
            # Stats
            st.metric("Mean Z-Score TB/U", f"{filtered_df['zsc_tbu'].mean():.2f}")
            st.metric("Std Dev", f"{filtered_df['zsc_tbu'].std():.2f}")
        
        with col4:
            fig_hist_bbtb = go.Figure()
            
            fig_hist_bbtb.add_trace(go.Histogram(
                x=filtered_df['zsc_bbtb'],
                nbinsx=40,
                marker_color='#2ecc71',
                opacity=0.75,
                name='BB/TB',
                hovertemplate='Z-Score: %{x:.2f}<br>Jumlah: %{y}<extra></extra>'
            ))
            
            fig_hist_bbtb.add_vline(x=-2, line_dash="dash", line_color="red", line_width=3,
                                   annotation_text="Batas Gizi Kurang", annotation_position="top")
            fig_hist_bbtb.add_vline(x=-3, line_dash="dot", line_color="darkred", line_width=2,
                                   annotation_text="Gizi Buruk", annotation_position="bottom")
            fig_hist_bbtb.add_vline(x=filtered_df['zsc_bbtb'].mean(), line_dash="solid",
                                   line_color="green", line_width=2,
                                   annotation_text=f"Mean: {filtered_df['zsc_bbtb'].mean():.2f}",
                                   annotation_position="top")
            
            fig_hist_bbtb.update_layout(
                title="Distribusi Z-Score BB/TB",
                xaxis_title="Z-Score BB/TB",
                yaxis_title="Frekuensi",
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_hist_bbtb, use_container_width=True)
            
            st.metric("Mean Z-Score BB/TB", f"{filtered_df['zsc_bbtb'].mean():.2f}")
            st.metric("Std Dev", f"{filtered_df['zsc_bbtb'].std():.2f}")
        
        with col5:
            fig_hist_bbu = go.Figure()
            
            fig_hist_bbu.add_trace(go.Histogram(
                x=filtered_df['zsc_bbu'],
                nbinsx=40,
                marker_color='#f39c12',
                opacity=0.75,
                name='BB/U',
                hovertemplate='Z-Score: %{x:.2f}<br>Jumlah: %{y}<extra></extra>'
            ))
            
            fig_hist_bbu.add_vline(x=-2, line_dash="dash", line_color="red", line_width=3,
                                  annotation_text="Batas BB Kurang", annotation_position="top")
            fig_hist_bbu.add_vline(x=-3, line_dash="dot", line_color="darkred", line_width=2,
                                  annotation_text="BB Sangat Kurang", annotation_position="bottom")
            fig_hist_bbu.add_vline(x=filtered_df['zsc_bbu'].mean(), line_dash="solid",
                                  line_color="green", line_width=2,
                                  annotation_text=f"Mean: {filtered_df['zsc_bbu'].mean():.2f}",
                                  annotation_position="top")
            
            fig_hist_bbu.update_layout(
                title="Distribusi Z-Score BB/U",
                xaxis_title="Z-Score BB/U",
                yaxis_title="Frekuensi",
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_hist_bbu, use_container_width=True)
            
            st.metric("Mean Z-Score BB/U", f"{filtered_df['zsc_bbu'].mean():.2f}")
            st.metric("Std Dev", f"{filtered_df['zsc_bbu'].std():.2f}")
        
        # Box plot perbandingan
        st.markdown("---")
        st.markdown("### 📦 Perbandingan Distribusi Z-Score")
        
        fig_box = go.Figure()
        
        fig_box.add_trace(go.Box(y=filtered_df['zsc_tbu'], name='TB/U',
                                marker_color='#3498db', boxmean='sd'))
        fig_box.add_trace(go.Box(y=filtered_df['zsc_bbtb'], name='BB/TB',
                                marker_color='#2ecc71', boxmean='sd'))
        fig_box.add_trace(go.Box(y=filtered_df['zsc_bbu'], name='BB/U',
                                marker_color='#f39c12', boxmean='sd'))
        
        fig_box.add_hline(y=-2, line_dash="dash", line_color="red", line_width=2)
        fig_box.add_hline(y=-3, line_dash="dot", line_color="darkred", line_width=2)
        
        fig_box.update_layout(
            title="Box Plot Perbandingan Z-Score",
            yaxis_title="Z-Score",
            template="plotly_white",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
    
    elif analysis_type == "Status Gizi":
        st.markdown("### 🍽️ Analisis Status Gizi Komprehensif")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📏 Status TB/U (Tinggi/Umur)")
            
            status_tbu = filtered_df['status_tbu'].value_counts()
            
            # Pie chart dengan styling yang lebih baik
            colors = ['#e74c3c', '#e67e22', '#f39c12', '#2ecc71', '#3498db']
            
            fig_tbu = go.Figure(data=[go.Pie(
                labels=status_tbu.index,
                values=status_tbu.values,
                hole=0.4,
                marker_colors=colors,
                textposition='auto',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
            )])
            
            fig_tbu.update_layout(
                title="Distribusi Status TB/U",
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig_tbu, use_container_width=True)
            
            # Metrics
            stunting_count = len(filtered_df[filtered_df['status_tbu'].isin(['Pendek', 'Sangat Pendek'])])
            st.metric("🔴 Total Pendek + Sangat Pendek", stunting_count,
                     delta=f"{(stunting_count/len(filtered_df)*100):.1f}%",
                     delta_color="inverse")
        
        with col2:
            st.markdown("#### ⚖️ Status BB/TB (Berat/Tinggi)")
            
            status_bbtb = filtered_df['status_bbtb'].value_counts()
            
            fig_bbtb = go.Figure(data=[go.Pie(
                labels=status_bbtb.index,
                values=status_bbtb.values,
                hole=0.4,
                marker_colors=colors,
                textposition='auto',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
            )])
            
            fig_bbtb.update_layout(
                title="Distribusi Status BB/TB",
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig_bbtb, use_container_width=True)
            
            gizi_kurang = len(filtered_df[filtered_df['status_bbtb'].str.contains('Kurang|Buruk', na=False)])
            st.metric("🟠 Total Gizi Kurang + Buruk", gizi_kurang,
                     delta=f"{(gizi_kurang/len(filtered_df)*100):.1f}%",
                     delta_color="inverse")
        
        with col3:
            st.markdown("#### 🏋️ Status BB/U (Berat/Umur)")
            
            status_bbu = filtered_df['status_bbu'].value_counts()
            
            fig_bbu = go.Figure(data=[go.Pie(
                labels=status_bbu.index,
                values=status_bbu.values,
                hole=0.4,
                marker_colors=colors,
                textposition='auto',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
            )])
            
            fig_bbu.update_layout(
                title="Distribusi Status BB/U",
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig_bbu, use_container_width=True)
            
            bb_kurang = len(filtered_df[filtered_df['status_bbu'].str.contains('Kurang', na=False)])
            st.metric("🟡 Total BB Kurang + Sangat Kurang", bb_kurang,
                     delta=f"{(bb_kurang/len(filtered_df)*100):.1f}%",
                     delta_color="inverse")
        
        st.markdown("---")
        
        # Crosstab analysis dengan styling lebih baik
        st.markdown("### 🔄 Hubungan Status TB/U dan BB/TB")
        st.caption("Analisis korelasi antara status tinggi badan dan berat badan balita")
        
        crosstab = pd.crosstab(filtered_df['status_tbu'], filtered_df['status_bbtb'], margins=True)
        
        # Heatmap yang lebih readable
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=crosstab.values,
            x=crosstab.columns,
            y=crosstab.index,
            colorscale='Reds',
            text=crosstab.values,
            texttemplate='%{text}',
            textfont={"size": 14},
            hovertemplate='TB/U: %{y}<br>BB/TB: %{x}<br>Jumlah: %{z}<extra></extra>',
            colorbar=dict(title="Jumlah<br>Balita")
        ))
        
        fig_heatmap.update_layout(
            title="Heatmap Hubungan Status TB/U dan BB/TB",
            xaxis_title="Status BB/TB",
            yaxis_title="Status TB/U",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Bar chart stacked untuk visualisasi alternatif
        st.markdown("### 📊 Visualisasi Stacked")
        
        crosstab_pct = pd.crosstab(filtered_df['status_tbu'], filtered_df['status_bbtb'], normalize='index') * 100
        
        fig_stacked = go.Figure()
        
        for col in crosstab_pct.columns:
            fig_stacked.add_trace(go.Bar(
                name=col,
                x=crosstab_pct.index,
                y=crosstab_pct[col],
                text=crosstab_pct[col].round(1),
                texttemplate='%{text}%',
                textposition='inside'
            ))
        
        fig_stacked.update_layout(
            barmode='stack',
            title="Distribusi Status BB/TB per Kategori TB/U (%)",
            xaxis_title="Status TB/U",
            yaxis_title="Persentase (%)",
            height=450,
            template="plotly_white",
            legend=dict(title="Status BB/TB")
        )
        
        st.plotly_chart(fig_stacked, use_container_width=True)
    
    elif analysis_type == "Perbandingan Puskesmas":
        st.markdown("### 🏥 Perbandingan Kinerja Antar Puskesmas")
        
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
        
        # Summary metrics
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        col_sum1.metric("Jumlah Puskesmas", len(pusk_stats))
        col_sum2.metric("Puskesmas Terbaik", 
                       pusk_stats.iloc[-1]['Puskesmas'],
                       delta=f"{pusk_stats.iloc[-1]['Persentase Stunting (%)']:.1f}%",
                       delta_color="inverse")
        col_sum3.metric("Puskesmas Prioritas",
                       pusk_stats.iloc[0]['Puskesmas'],
                       delta=f"{pusk_stats.iloc[0]['Persentase Stunting (%)']:.1f}%",
                       delta_color="inverse")
        col_sum4.metric("Rentang Prevalensi",
                       f"{pusk_stats['Persentase Stunting (%)'].min():.1f}% - {pusk_stats['Persentase Stunting (%)'].max():.1f}%")
        
        st.markdown("---")
        
        # Bar chart yang lebih informatif
        st.markdown("#### 📊 Persentase Stunting per Puskesmas")
        
        fig_pusk_pct = go.Figure()
        
        colors_bar = ['#e74c3c' if x > 20 else '#f39c12' if x > 10 else '#2ecc71' 
                     for x in pusk_stats['Persentase Stunting (%)']]
        
        fig_pusk_pct.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Persentase Stunting (%)'],
            marker_color=colors_bar,
            text=pusk_stats['Persentase Stunting (%)'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         'Persentase: %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        fig_pusk_pct.add_hline(y=pusk_stats['Persentase Stunting (%)'].mean(),
                              line_dash="dash", line_color="red", line_width=2,
                              annotation_text=f"Rata-rata: {pusk_stats['Persentase Stunting (%)'].mean():.1f}%",
                              annotation_position="right")
        
        fig_pusk_pct.update_layout(
            title="Prevalensi Stunting per Puskesmas",
            xaxis_title="Puskesmas",
            yaxis_title="Persentase Stunting (%)",
            xaxis_tickangle=-45,
            height=500,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig_pusk_pct, use_container_width=True)
        
        st.markdown("---")
        
        # Comparison table dengan conditional formatting
        st.markdown("#### 📋 Tabel Perbandingan Detail")
        
        # Style dataframe
        def color_scale(val):
            if val > 20:
                return 'background-color: #ffcccc'
            elif val > 10:
                return 'background-color: #ffe6cc'
            else:
                return 'background-color: #ccffcc'
        
        styled_df = pusk_stats.style.applymap(
            color_scale,
            subset=['Persentase Stunting (%)']
        ).format({
            'Persentase Stunting (%)': '{:.2f}%',
            'Rata-rata Z-Score TB/U': '{:.2f}',
            'Rata-rata Z-Score BB/TB': '{:.2f}',
            'Rata-rata Z-Score BB/U': '{:.2f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
        
        st.markdown("---")
        
        # Z-Score comparison dengan grouped bar
        st.markdown("#### 📈 Perbandingan Rata-rata Z-Score")
        st.caption("Semakin rendah Z-Score, semakin buruk status gizi")
        
        fig_zscore_compare = go.Figure()
        
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score TB/U'],
            name='TB/U',
            marker_color='#3498db',
            text=pusk_stats['Rata-rata Z-Score TB/U'].round(2),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Z-Score TB/U: %{y:.2f}<extra></extra>'
        ))
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score BB/TB'],
            name='BB/TB',
            marker_color='#2ecc71',
            text=pusk_stats['Rata-rata Z-Score BB/TB'].round(2),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Z-Score BB/TB: %{y:.2f}<extra></extra>'
        ))
        fig_zscore_compare.add_trace(go.Bar(
            x=pusk_stats['Puskesmas'],
            y=pusk_stats['Rata-rata Z-Score BB/U'],
            name='BB/U',
            marker_color='#f39c12',
            text=pusk_stats['Rata-rata Z-Score BB/U'].round(2),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Z-Score BB/U: %{y:.2f}<extra></extra>'
        ))
        
        fig_zscore_compare.add_hline(y=-2, line_dash="dash", line_color="red", line_width=2,
                                     annotation_text="Batas Normal (Z=-2)", annotation_position="right")
        fig_zscore_compare.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)
        
        fig_zscore_compare.update_layout(
            title="Rata-rata Z-Score per Puskesmas (Grouped)",
            xaxis_title="Puskesmas",
            yaxis_title="Z-Score",
            xaxis_tickangle=-45,
            barmode='group',
            height=550,
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_zscore_compare, use_container_width=True)
        
        # Radar chart untuk perbandingan multi-dimensi
        st.markdown("#### 🎯 Radar Chart Perbandingan")
        st.caption("Visualisasi multi-dimensi kinerja puskesmas")
        
        # Normalize untuk radar chart
        pusk_radar = pusk_stats.head(5).copy()  # Top 5 puskesmas
        
        fig_radar = go.Figure()
        
        for idx, row in pusk_radar.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    row['Total Balita'] / pusk_radar['Total Balita'].max() * 100,
                    100 - row['Persentase Stunting (%)'],  # Inverted (higher is better)
                    (row['Rata-rata Z-Score TB/U'] + 5) / 5 * 100,  # Normalized
                    (row['Rata-rata Z-Score BB/TB'] + 5) / 5 * 100,
                    (row['Rata-rata Z-Score BB/U'] + 5) / 5 * 100
                ],
                theta=['Cakupan<br>Sampel', 'Tingkat<br>Kesehatan', 'Z-Score<br>TB/U', 
                       'Z-Score<br>BB/TB', 'Z-Score<br>BB/U'],
                fill='toself',
                name=row['Puskesmas']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=600,
            showlegend=True,
            title="Perbandingan Multi-Dimensi (Top 5 Puskesmas)"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    else:  # Tren Temporal
        st.markdown("### 📅 Analisis Tren Temporal")
        st.caption("Perkembangan kasus stunting dari waktu ke waktu")
        
        # Group by date dengan periode yang lebih detail
        temporal_data = filtered_df.groupby(filtered_df['tgl_pengambilan_data'].dt.to_period('M')).agg({
            'nama_balita': 'count',
            'stunting_balita': lambda x: (x == 'Ya').sum()
        }).reset_index()
        
        temporal_data['tgl_pengambilan_data'] = temporal_data['tgl_pengambilan_data'].dt.to_timestamp()
        temporal_data.columns = ['Bulan', 'Total Balita', 'Jumlah Stunting']
        temporal_data['Persentase Stunting'] = (temporal_data['Jumlah Stunting'] / temporal_data['Total Balita'] * 100).round(2)
        temporal_data = temporal_data.sort_values('Bulan')
        
        # Summary metrics
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        
        col_t1.metric("Total Periode", f"{len(temporal_data)} bulan")
        col_t2.metric("Rata-rata Kasus/Bulan", f"{temporal_data['Jumlah Stunting'].mean():.1f}")
        col_t3.metric("Bulan Tertinggi", 
                     temporal_data.loc[temporal_data['Jumlah Stunting'].idxmax(), 'Bulan'].strftime('%b %Y'))
        col_t4.metric("Total Kasus", f"{temporal_data['Jumlah Stunting'].sum():,}")
        
        st.markdown("---")
        
        # Line chart yang lebih informatif dengan dual axis
        st.markdown("#### 📈 Tren Kasus dan Persentase Stunting")
        
        fig_trend = make_subplots(
            specs=[[{"secondary_y": True}]]
        )
        
        # Jumlah kasus (primary y-axis)
        fig_trend.add_trace(
            go.Scatter(
                x=temporal_data['Bulan'],
                y=temporal_data['Jumlah Stunting'],
                mode='lines+markers',
                name='Jumlah Kasus',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=10, symbol='circle'),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)',
                hovertemplate='<b>%{x|%B %Y}</b><br>Kasus: %{y}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Persentase (secondary y-axis)
        fig_trend.add_trace(
            go.Scatter(
                x=temporal_data['Bulan'],
                y=temporal_data['Persentase Stunting'],
                mode='lines+markers',
                name='Persentase (%)',
                line=dict(color='#3498db', width=3, dash='dash'),
                marker=dict(size=10, symbol='diamond'),
                hovertemplate='<b>%{x|%B %Y}</b><br>Persentase: %{y:.2f}%<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Average lines
        avg_kasus = temporal_data['Jumlah Stunting'].mean()
        avg_persen = temporal_data['Persentase Stunting'].mean()
        
        fig_trend.add_hline(y=avg_kasus, line_dash="dot", line_color="red",
                           annotation_text=f"Rata-rata Kasus: {avg_kasus:.1f}",
                           secondary_y=False)
        fig_trend.add_hline(y=avg_persen, line_dash="dot", line_color="blue",
                           annotation_text=f"Rata-rata %: {avg_persen:.1f}%",
                           secondary_y=True, annotation_position="bottom right")
        
        fig_trend.update_xaxes(title_text="Periode")
        fig_trend.update_yaxes(title_text="<b>Jumlah Kasus</b>", secondary_y=False)
        fig_trend.update_yaxes(title_text="<b>Persentase (%)</b>", secondary_y=True)
        
        fig_trend.update_layout(
            title="Tren Kasus Stunting Dari Waktu ke Waktu",
            hovermode='x unified',
            height=500,
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("---")
        
        # Area chart untuk total sampel
        st.markdown("#### 📊 Volume Sampel Bulanan")
        
        fig_area = go.Figure()
        
        fig_area.add_trace(go.Scatter(
            x=temporal_data['Bulan'],
            y=temporal_data['Total Balita'],
            mode='lines',
            name='Total Balita',
            line=dict(color='#9b59b6', width=2),
            fill='tozeroy',
            fillcolor='rgba(155, 89, 182, 0.3)',
            hovertemplate='<b>%{x|%B %Y}</b><br>Total Sampel: %{y}<extra></extra>'
        ))
        
        fig_area.update_layout(
            title="Volume Sampel Balita per Bulan",
            xaxis_title="Periode",
            yaxis_title="Jumlah Balita",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_area, use_container_width=True)
        
        st.markdown("---")
        
        # Data table dengan formatting
        st.markdown("#### 📋 Tabel Data Temporal")
        
        temporal_display = temporal_data.copy()
        temporal_display['Bulan'] = temporal_display['Bulan'].dt.strftime('%B %Y')
        
        # Add trend indicators
        temporal_display['Trend'] = ''
        for i in range(1, len(temporal_display)):
            if temporal_display.iloc[i]['Jumlah Stunting'] > temporal_display.iloc[i-1]['Jumlah Stunting']:
                temporal_display.at[i, 'Trend'] = '📈 Naik'
            elif temporal_display.iloc[i]['Jumlah Stunting'] < temporal_display.iloc[i-1]['Jumlah Stunting']:
                temporal_display.at[i, 'Trend'] = '📉 Turun'
            else:
                temporal_display.at[i, 'Trend'] = '➡️ Stabil'
        
        st.dataframe(
            temporal_display.style.format({
                'Persentase Stunting': '{:.2f}%'
            }),
            use_container_width=True
        )
        
        # Statistical summary
        st.markdown("#### 📊 Ringkasan Statistik")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.write("**Kasus Stunting**")
            st.write(f"- Min: {temporal_data['Jumlah Stunting'].min()}")
            st.write(f"- Max: {temporal_data['Jumlah Stunting'].max()}")
            st.write(f"- Std Dev: {temporal_data['Jumlah Stunting'].std():.2f}")
        
        with col_stat2:
            st.write("**Persentase (%)**")
            st.write(f"- Min: {temporal_data['Persentase Stunting'].min():.2f}%")
            st.write(f"- Max: {temporal_data['Persentase Stunting'].max():.2f}%")
            st.write(f"- Std Dev: {temporal_data['Persentase Stunting'].std():.2f}%")
        
        with col_stat3:
            st.write("**Total Sampel**")
            st.write(f"- Min: {temporal_data['Total Balita'].min()}")
            st.write(f"- Max: {temporal_data['Total Balita'].max()}")
            st.write(f"- Std Dev: {temporal_data['Total Balita'].std():.2f}")

else:
    st.error("❌ Data tidak dapat dimuat.")
    st.info("Pastikan file data tersedia di: data/data_skrinning_stunting(1).csv")
