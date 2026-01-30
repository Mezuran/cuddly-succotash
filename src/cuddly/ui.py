import streamlit as st
import altair as alt

from cuddly.utils import load_data
from cuddly.components import maps, charts, tables

st.set_page_config(layout="centered", page_title="PDS: Analisis Harga iPhone")

df = load_data()
if df is None:
    st.error("Data tidak ditemukan. Pastikan file CSV ada.")
    st.stop()

st.title("Pasar iPhone Bekas")
st.markdown("""
Visualisasi data penjual iPhone bekas/baru dari OLX dan Tokopedia. Peta di bawah menggunakan choropleth map berdasarkan jumlah listing per Provinsi.

List Poin Penjelasan:
- Visualisasi
- GIS (Geographical Information System)
""")

st.markdown("---")

with st.container():
    available_series = ["iPhone 11", "iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15", "iPhone 16"]
    series_select = st.selectbox("Pilih Seri yang ingin dianalisis:", available_series)

filtered = df[df["Model"].str.contains(series_select, na=False, case=False)].copy()

tab1, tab2, tab3 = st.tabs(["Charts", "Map", "Dataset"])
with tab1:
    charts.render_variant_breakdown(filtered)

with tab2:
    st.subheader(f"Sebaran Lokasi Penjual {series_select}")
    maps.render_map(filtered)

with tab3:
    st.subheader(f"Dataset {series_select}")
    tables.render_datatable(filtered)