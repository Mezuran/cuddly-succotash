import streamlit as st

def render_datatable(df):
    st.caption("Daftar lengkap data.")
    st.dataframe(
        df[['Judul', 'Model', 'Kategori', 'Harga', 'Lokasi', 'Toko', 'Provinsi']],
        column_config={
            "Judul": st.column_config.TextColumn("Judul Barang", width="large"),
            "Harga": st.column_config.TextColumn("Harga IDR"),
            "Toko": st.column_config.TextColumn("Nama Toko"),
        },
        width='content',
        hide_index=True
    )