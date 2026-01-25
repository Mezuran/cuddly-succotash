import streamlit as st
import pandas as pd

from typing import Optional
from pathlib import Path

def get_province(city_name):
    CITY_TO_PROV = {
        'Jakarta Selatan': 'DKI JAKARTA', 'Jakarta Barat': 'DKI JAKARTA',
        'Jakarta Pusat': 'DKI JAKARTA', 'Jakarta Timur': 'DKI JAKARTA', 
        'Jakarta Utara': 'DKI JAKARTA', 'DKI Jakarta': 'DKI JAKARTA',
        'Bandung': 'JAWA BARAT', 'Bandung Kota': 'JAWA BARAT', 'Kab. Bandung': 'JAWA BARAT',
        'Bekasi': 'JAWA BARAT', 'Bekasi Kota': 'JAWA BARAT', 'Kab. Bekasi': 'JAWA BARAT',
        'Bogor': 'JAWA BARAT', 'Bogor Kota': 'JAWA BARAT', 'Kab. Bogor': 'JAWA BARAT',
        'Depok': 'JAWA BARAT', 'Depok Kota': 'JAWA BARAT', 'Cimahi': 'JAWA BARAT', 'Karawang': 'JAWA BARAT',
        'Tangerang': 'BANTEN', 'Tangerang Kota': 'BANTEN', 'Tangerang Selatan': 'BANTEN', 
        'Kab. Tangerang': 'BANTEN', 'Banten': 'BANTEN',
        'Semarang': 'JAWA TENGAH', 'Semarang Kota': 'JAWA TENGAH', 'Surakarta': 'JAWA TENGAH', 
        'Solo': 'JAWA TENGAH', 'Banyumas': 'JAWA TENGAH',
        'Yogyakarta': 'DI YOGYAKARTA', 'Yogyakarta Kota': 'DI YOGYAKARTA', 
        'Sleman': 'DI YOGYAKARTA', 'Bantul': 'DI YOGYAKARTA',
        'Surabaya': 'JAWA TIMUR', 'Surabaya Kota': 'JAWA TIMUR', 'Malang': 'JAWA TIMUR', 
        'Sidoarjo': 'JAWA TIMUR', 'Jember': 'JAWA TIMUR',
        'Bali': 'BALI', 'Denpasar': 'BALI', 'Badung': 'BALI',
        'Medan': 'SUMATERA UTARA', 'Palembang': 'SUMATERA SELATAN', 'Makassar': 'SULAWESI SELATAN',
        'Batam': 'KEPULAUAN RIAU', 'Pekanbaru': 'RIAU', 'Pontianak': 'KALIMANTAN BARAT',
        'Kab. Biak Numfor': 'PAPUA', 'Papua': 'PAPUA'
    }
    city_name = str(city_name).strip()
    if city_name in CITY_TO_PROV:
        return CITY_TO_PROV[city_name]
    for key, val in CITY_TO_PROV.items():
        if key.lower() in city_name.lower():
            return val
    return "Lainnya"

@st.cache_data
def load_data() -> Optional[pd.DataFrame]:
    result = []

    file_path = Path(f"iphone_tokopedia_cleaned.csv")
    if not file_path.exists():
        file_path = Path(f"./data/iphone_tokopedia_cleaned.csv")

    if not file_path.exists():
        return None

    df = pd.read_csv(file_path)
    result.append(df)

    if not result:
        return None
    
    df = pd.concat(result, ignore_index=True)
    df = df[df['Lokasi'] != '-']
    df['Provinsi'] = df['Lokasi'].apply(get_province)
    
    df = df[(df['Harga_Int'] > 1000000) & (df['Harga_Int'] < 100000000)]
    
    return df

def analyze_price_fairness(row, stats):
    model = row['Model']
    cat = row['Kategori']
    price = row['Harga_Int']
    
    if model in stats and cat in stats[model]:
        s = stats[model][cat]
        if price < s['lower_bound']: return "Terlalu Murah"
        elif price > s['upper_bound']: return "Terlalu Mahal"
        else: return "Wajar"
    return "-"