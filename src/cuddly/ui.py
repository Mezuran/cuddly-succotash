import streamlit as st
import pandas as pd
import folium

from streamlit_folium import st_folium
from pathlib import Path
from typing import Optional

def get_province(city_name):
    CITY_TO_PROV = {
        # DKI Jakarta (Biasanya di GeoJSON tertulis DKI JAKARTA)
        'Jakarta Selatan': 'DKI JAKARTA', 'Jakarta Barat': 'DKI JAKARTA',
        'Jakarta Pusat': 'DKI JAKARTA', 'Jakarta Timur': 'DKI JAKARTA', 
        'Jakarta Utara': 'DKI JAKARTA', 'DKI Jakarta': 'DKI JAKARTA',
        
        # Jawa Barat
        'Bandung': 'JAWA BARAT', 'Bandung Kota': 'JAWA BARAT', 'Kab. Bandung': 'JAWA BARAT',
        'Bekasi': 'JAWA BARAT', 'Bekasi Kota': 'JAWA BARAT', 'Kab. Bekasi': 'JAWA BARAT',
        'Bogor': 'JAWA BARAT', 'Bogor Kota': 'JAWA BARAT', 'Kab. Bogor': 'JAWA BARAT',
        'Depok': 'JAWA BARAT', 'Depok Kota': 'JAWA BARAT', 'Cimahi': 'JAWA BARAT', 'Karawang': 'JAWA BARAT',
        
        # Banten
        'Tangerang': 'BANTEN', 'Tangerang Kota': 'BANTEN', 'Tangerang Selatan': 'BANTEN', 
        'Kab. Tangerang': 'BANTEN', 'Banten': 'BANTEN',
        
        # Jawa Tengah
        'Semarang': 'JAWA TENGAH', 'Semarang Kota': 'JAWA TENGAH', 'Surakarta': 'JAWA TENGAH', 
        'Solo': 'JAWA TENGAH', 'Banyumas': 'JAWA TENGAH',
        
        # DI Yogyakarta (Nama di GeoJSON seringkali 'DAERAH ISTIMEWA YOGYAKARTA' atau 'DI YOGYAKARTA')
        # Kita coba format standar
        'Yogyakarta': 'DI YOGYAKARTA', 'Yogyakarta Kota': 'DI YOGYAKARTA', 
        'Sleman': 'DI YOGYAKARTA', 'Bantul': 'DI YOGYAKARTA',
        
        # Jawa Timur
        'Surabaya': 'JAWA TIMUR', 'Surabaya Kota': 'JAWA TIMUR', 'Malang': 'JAWA TIMUR', 
        'Sidoarjo': 'JAWA TIMUR', 'Jember': 'JAWA TIMUR',
        
        # Bali
        'Bali': 'BALI', 'Denpasar': 'BALI', 'Badung': 'BALI',
        
        # Sumatera & Lainnya
        'Medan': 'SUMATERA UTARA', 
        'Palembang': 'SUMATERA SELATAN', 
        'Makassar': 'SULAWESI SELATAN',
        'Batam': 'KEPULAUAN RIAU', 
        'Pekanbaru': 'RIAU', 
        'Pontianak': 'KALIMANTAN BARAT',
        'Kab. Biak Numfor': 'PAPUA', 'Papua': 'PAPUA'
    }

    city_name = str(city_name).strip()
    # Cek match langsung
    if city_name in CITY_TO_PROV:
        return CITY_TO_PROV[city_name]
    # Cek partial match (misal "Kota Bandung" -> "Bandung")
    for key, val in CITY_TO_PROV.items():
        if key.lower() in city_name.lower():
            return val
    return "Lainnya"

@st.cache_data
def load_data() -> Optional[pd.DataFrame]:
    ecommerce = ['olx', 'tokopedia']
    result = []

    for i in ecommerce:
        file_path = Path(f"./data/iphone_{i}.csv") 
        if not file_path.exists():
            st.warning(f"File {file_path} tidak ditemukan, dilewati.")
            continue
        
        df = pd.read_csv(file_path)
        df['platform'] = i
        result.append(df)

    if not result:
        return None
    
    df = pd.concat(result, ignore_index=True)
    df = df[df['Lokasi'] != '-']
    df['Provinsi'] = df['Lokasi'].apply(get_province)

    return df

df = load_data()

st.set_page_config(layout="wide", page_title="PDS: Tugas Besar")

col_hero_1, col_hero_2 = st.columns([2, 1]) 

with col_hero_1:
    st.markdown("""
        # Data Provinsi Penjual iPhone Terbanyak di Indonesia
                
        Visualisasi data penjual iPhone bekas/baru dari OLX dan Tokopedia.
        Peta di bawah menggunakan choropleth map berdasarkan jumlah listing per Provinsi.
                
        List Poin Penjelasan:
        - Visualisasi
        - GIS (Geographical Information System)
    """)

with col_hero_2:
    st.image("resources/hero_image.png")

st.markdown("---")

if df is not None:
    col_input_1, col_input_2 = st.columns([1, 3])
    with col_input_1:
        jenis = st.selectbox("Pilih Jenis iPhone", ["iPhone 11", "iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15", "iPhone 16"])

    filtered = df[df["Model"].str.contains(jenis, na=False, case=False)]

    st.subheader("Peta Persebaran (GIS)")
    st.caption(f"Menampilkan jumlah listing {jenis} per Provinsi.")

    map_data = filtered['Provinsi'].value_counts().reset_index()
    map_data.columns = ['propinsi', 'count']

    geojson_url = "https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/refs/heads/master/indonesia-prov.geojson"

    m = folium.Map(location=[-2.5489, 118.0149], zoom_start=4)

    folium.Choropleth(
        geo_data=geojson_url,
        name="choropleth",
        data=map_data,
        columns=["propinsi", "count"],
        key_on="feature.properties.Propinsi", 
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        nan_fill_color="white"
    ).add_to(m)

    st_folium(m, use_container_width=True, height=500, returned_objects=[])
    
    if 'Kategori' in filtered.columns:
        c1, c2 = st.columns([9, 1])
        with c1:
            chart_data = pd.crosstab(filtered['Model'], filtered['Kategori'])
            valid_cols = [c for c in ['iBox', 'Inter', 'Cukai'] if c in chart_data.columns]
            st.write(f"Chart {jenis}")
            st.bar_chart(chart_data[valid_cols] if valid_cols else chart_data, stack=False)
        with c2:
            st.write("Total per Kategori:")
            st.dataframe(chart_data.T, width='content')
    else:
        st.warning("Kolom 'Kategori' tidak ditemukan dalam data.")

    col_1, col_2 = st.columns([9, 1]) 
    with col_1:
        st.write('Detail Data')
        st.dataframe(
            filtered[['Judul', 'Harga', 'Provinsi', 'platform', 'Lokasi']].head(100),
            column_config={
                "Judul": st.column_config.TextColumn("Judul Iklan", width="large"),
                "Harga": st.column_config.TextColumn("Harga"),
                "Provinsi": st.column_config.TextColumn("Provinsi", width="medium"),
                "platform": st.column_config.TextColumn("Apps", width="small"),
            },
            width='content',
            hide_index=True
        )
    with col_2:
        st.write('Jumlah')
        st.dataframe(
            map_data, 
            column_config={
                "propinsi": "Provinsi",
                "count": st.column_config.NumberColumn("Jumlah", format="%d")
            },
            hide_index=True,
            width='content'
        )
else:
    st.error("Gagal memuat data. Pastikan file CSV tersedia di folder ./data/")