# pages/4_Data_Lengkap.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Stunting", page_icon="📋", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data_skrinning_stunting(1).csv')
        df['tgl_pengambilan_data'] = pd.to_datetime(df['tgl_pengambilan_data'], format='%m/%d/%Y', errors='coerce')
        df['tgl_lahir_balita'] = pd.to_datetime(df['tgl_lahir_balita'], errors='coerce')
        df['tgl_lahir_responden'] = pd.to_datetime(df['tgl_lahir_responden'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_data()

if df is not None:
    st.title("📋 Data Lengkap Skrining Stunting")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    
    # Kecamatan filter
    kecamatan_list = ['Semua'] + sorted(df['nama_kecamatan'].dropna().unique().tolist())
    selected_kecamatan = st.sidebar.multiselect(
        "Kecamatan",
        options=kecamatan_list,
        default=['Semua']
    )
    
    # Puskesmas filter
    if 'Semua' not in selected_kecamatan and selected_kecamatan:
        puskesmas_options = df[df['nama_kecamatan'].isin(selected_kecamatan)]['nama_puskesmas'].unique()
    else:
        puskesmas_options = df['nama_puskesmas'].unique()
    
    puskesmas_list = ['Semua'] + sorted(puskesmas_options.tolist())
    selected_puskesmas = st.sidebar.multiselect(
        "Puskesmas",
        options=puskesmas_list,
        default=['Semua']
    )
    
    # Status stunting filter
    stunting_status = st.sidebar.multiselect(
        "Status Stunting",
        options=['Ya', 'Tidak'],
        default=['Ya', 'Tidak']
    )
    
    # Gender filter
    gender_filter = st.sidebar.multiselect(
        "Jenis Kelamin",
        options=df['jenis_kelamin_balita'].unique().tolist(),
        default=df['jenis_kelamin_balita'].unique().tolist()
    )
    
    # Status TB/U filter
    status_tbu_options = ['Semua'] + df['status_tbu'].dropna().unique().tolist()
    selected_status_tbu = st.sidebar.multiselect(
        "Status TB/U",
        options=status_tbu_options,
        default=['Semua']
    )
    
    # Date range filter
    st.sidebar.markdown("### 📅 Rentang Tanggal")
    date_min = df['tgl_pengambilan_data'].min()
    date_max = df['tgl_pengambilan_data'].max()
    
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'Semua' not in selected_kecamatan:
        filtered_df = filtered_df[filtered_df['nama_kecamatan'].isin(selected_kecamatan)]
    
    if 'Semua' not in selected_puskesmas:
        filtered_df = filtered_df[filtered_df['nama_puskesmas'].isin(selected_puskesmas)]
    
    if stunting_status:
        filtered_df = filtered_df[filtered_df['stunting_balita'].isin(stunting_status)]
    
    if gender_filter:
        filtered_df = filtered_df[filtered_df['jenis_kelamin_balita'].isin(gender_filter)]
    
    if 'Semua' not in selected_status_tbu:
        filtered_df = filtered_df[filtered_df['status_tbu'].isin(selected_status_tbu)]
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['tgl_pengambilan_data'].dt.date >= date_range[0]) &
            (filtered_df['tgl_pengambilan_data'].dt.date <= date_range[1])
        ]
    
    # Statistics
    st.markdown("### 📊 Statistik Data Terfilter")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Records", f"{len(filtered_df):,}")
    with col2:
        stunting_count = len(filtered_df[filtered_df['stunting_balita'] == 'Ya'])
        st.metric("Stunting", f"{stunting_count:,}")
    with col3:
        pct = (stunting_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("Persentase", f"{pct:.1f}%")
    with col4:
        st.metric("Kecamatan", filtered_df['nama_kecamatan'].nunique())
    with col5:
        st.metric("Puskesmas", filtered_df['nama_puskesmas'].nunique())
    
    st.markdown("---")
    
    # Search functionality
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        search_term = st.text_input("🔍 Cari data (nama balita, NIK, nama responden, dll)", "")
    with col_search2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_columns = st.multiselect(
            "Kolom pencarian",
            options=['nama_balita', 'nik_balita', 'nama_responden', 'nama_desa'],
            default=['nama_balita']
        )
    
    # Apply search
    display_df = filtered_df.copy()
    if search_term and search_columns:
        mask = display_df[search_columns].astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]
    
    # Column selection
    st.markdown("### 🎯 Pilih Kolom untuk Ditampilkan")
    
    available_columns = display_df.columns.tolist()
    default_columns = [
        'tgl_pengambilan_data', 'nama_balita', 'umur_balita', 'jenis_kelamin_balita',
        'stunting_balita', 'status_tbu', 'status_bbtb', 'status_bbu',
        'nama_kecamatan', 'nama_desa', 'nama_puskesmas'
    ]
    
    # Filter default columns to only include those that exist
    default_columns = [col for col in default_columns if col in available_columns]
    
    selected_columns = st.multiselect(
        "Pilih kolom yang ingin ditampilkan",
        options=available_columns,
        default=default_columns
    )
    
    if not selected_columns:
        st.warning("⚠️ Pilih minimal satu kolom untuk ditampilkan")
    else:
        # Display dataframe
        st.markdown(f"### 📄 Data Tabel ({len(display_df)} records)")
        
        # Format dates for display
        display_df_formatted = display_df[selected_columns].copy()
        for col in display_df_formatted.columns:
            if display_df_formatted[col].dtype == 'datetime64[ns]':
                display_df_formatted[col] = display_df_formatted[col].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df_formatted,
            use_container_width=True,
            height=500
        )
        
        # Download options
        st.markdown("### 💾 Download Data")
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        with col_dl1:
            # CSV download
            csv = display_df[selected_columns].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"data_stunting_sidoarjo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_dl2:
            # Excel download
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                display_df[selected_columns].to_excel(writer, index=False, sheet_name='Data Stunting')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"data_stunting_sidoarjo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_dl3:
            # JSON download
            json_data = display_df[selected_columns].to_json(orient='records', date_format='iso')
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"data_stunting_sidoarjo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Summary statistics
        if len(display_df) > 0:
            st.markdown("### 📈 Ringkasan Statistik")
            
            tab1, tab2, tab3 = st.tabs(["📊 Status Stunting", "👥 Demografi", "📍 Wilayah"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Status Stunting**")
                    stunting_summary = display_df['stunting_balita'].value_counts()
                    st.dataframe(stunting_summary, use_container_width=True)
                
                with col2:
                    st.markdown("**Status TB/U**")
                    tbu_summary = display_df['status_tbu'].value_counts()
                    st.dataframe(tbu_summary, use_container_width=True)
            
            with tab2:
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**Jenis Kelamin**")
                    gender_summary = display_df['jenis_kelamin_balita'].value_counts()
                    st.dataframe(gender_summary, use_container_width=True)
                
                with col4:
                    st.markdown("**Distribusi Umur (Top 10)**")
                    age_summary = display_df['umur_balita'].value_counts().head(10)
                    st.dataframe(age_summary, use_container_width=True)
            
            with tab3:
                col5, col6 = st.columns(2)
                with col5:
                    st.markdown("**Kecamatan**")
                    kec_summary = display_df['nama_kecamatan'].value_counts()
                    st.dataframe(kec_summary, use_container_width=True)
                
                with col6:
                    st.markdown("**Puskesmas**")
                    pusk_summary = display_df['nama_puskesmas'].value_counts()
                    st.dataframe(pusk_summary, use_container_width=True)

else:
    st.error("❌ Data tidak dapat dimuat. Pastikan file CSV tersedia.")