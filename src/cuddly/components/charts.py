import streamlit as st
import altair as alt
import pandas as pd
import re

from cuddly.utils import analyze_price_fairness

def render_chart_wajar(filtered):
    price_stats = {}
    valid_categories = [c for c in ['iBox', 'Inter', 'Cukai'] if c in filtered['Kategori'].unique()]

    for cat in valid_categories:
        cat_data = filtered[filtered['Kategori'] == cat]
        if not cat_data.empty:
            prices = cat_data['Harga_Int'].dropna()
            q1 = prices.quantile(0.25)
            q3 = prices.quantile(0.75)
            iqr = q3 - q1
            price_stats[cat] = {
                'lower_bound': max(0, q1 - 1.5 * iqr),
                'upper_bound': q3 + 1.5 * iqr
            }

    # Labeling Data di Tabel
    if price_stats:
        filtered['Status Harga'] = filtered.apply(lambda x: analyze_price_fairness(x, price_stats), axis=1)
    else:
        filtered['Status Harga'] = "-"

    # --- SECTION CHART HARGA (BOX PLOT) ---
    st.subheader(f"Rentang Harga Wajar")
    st.caption("Grafik Box Plot: Kotak menunjukkan rentang harga wajar. Titik-titik di luar garis adalah harga tidak wajar (potensi penipuan/rusak atau kemahalan).")

    # Membuat Chart Box Plot dengan Altair
    # Boxplot secara otomatis menghitung Q1, Q3, Median, dan Outliers
    chart_price = alt.Chart(filtered).mark_boxplot(extent=1.5, size=50).encode(
        x=alt.X('Kategori:N', title=None),
        y=alt.Y('Harga_Int:Q', title='Harga (Rp)', axis=alt.Axis(format=',.0f')),
        color=alt.Color('Kategori:N', legend=None),
        tooltip=['Judul', 'Harga', 'Lokasi'] # Tooltip agar titik outlier bisa dicek isinya apa
    ).properties(
        height=400
    ).interactive()

    st.altair_chart(chart_price, use_container_width=True)

def clean_terjual(val):
    """
    Membersihkan data kolom 'Terjual' menjadi angka numeric.
    Contoh: '250+ terjual' -> 250, '2rb+ terjual' -> 2000
    """
    s = str(val).lower()
    if 'rb' in s:
        s = s.replace(',', '.').replace('+', '').replace(' terjual', '').strip()
        num_part = re.search(r'[\d\.]+', s)
        if num_part:
            try:
                return int(float(num_part.group()) * 1000)
            except:
                return 0
        return 0
    
    digits = re.findall(r'\d+', s)
    if digits:
        return int(digits[0])
    return 0

def render_charts(df):
    st.caption("Rata-rata harga pasar per model.")
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Model', sort='-y', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('mean(Harga_Int):Q', title='Rata-rata Harga (IDR)'),
        color='Model',
        tooltip=[
            alt.Tooltip('Model', title='Model'),
            alt.Tooltip('mean(Harga_Int):Q', format=',.0f', title='Harga Rata-rata'),
            alt.Tooltip('count():Q', title='Jumlah Barang')
        ]
    ).interactive()

    st.altair_chart(chart, width='stretch')

def render_category_charts(df):
    st.caption("Analisis perbandingan antara Inter, iBox, dan Cukai.")
    
    base = alt.Chart(df).encode(
        x=alt.X('Kategori', axis=alt.Axis(labelAngle=0, title=None))
    )
    
    price_chart = base.mark_bar().encode(
        y=alt.Y('mean(Harga_Int):Q', title='Rata-rata Harga (IDR)'),
        color=alt.Color('Kategori', legend=None),
        tooltip=['Kategori', alt.Tooltip('mean(Harga_Int):Q', format=',.0f', title='Rata-rata')]
    ).properties(title="Rata-rata Harga")

    count_chart = base.mark_bar().encode(
        y=alt.Y('count():Q', title='Jumlah Unit'),
        color=alt.Color('Kategori', legend=None),
        tooltip=['Kategori', alt.Tooltip('count():Q', title='Jumlah')]
    ).properties(title="Ketersediaan Stok")

    c1, c2 = st.columns(2)
    with c1: st.altair_chart(price_chart, width='stretch')
    with c2: st.altair_chart(count_chart, width='stretch')

def render_scam_analysis(df):
    st.subheader("Analisis Deteksi Scam & Harga Wajar")
    st.caption("Matriks perbandingan Harga vs Jumlah Terjual.")

    if df.empty:
        st.warning("Data tidak cukup.")
        return

    # 1. Persiapan Data
    df_chart = df.copy()
    df_chart['Terjual_Count'] = df_chart['Terjual'].apply(clean_terjual)
    
    mean_price = df_chart['Harga_Int'].mean()
    std_dev = df_chart['Harga_Int'].std()
    
    lower_bound = mean_price - (1.0 * std_dev)
    upper_bound = mean_price + (1.0 * std_dev)

    hard_limit_low = mean_price * 0.5 
    
    if lower_bound < hard_limit_low:
        lower_bound = hard_limit_low

    # Kategorisasi
    def get_status(price):
        if price < lower_bound: return "Indikasi Scam / Rusak"
        elif price > upper_bound: return "Kemahalan"
        return "Harga Wajar"
    
    df_chart['Status'] = df_chart['Harga_Int'].apply(get_status)

    # Menampilkan Info Threshold
    c1, c2, c3 = st.columns(3)
    c1.metric("Batas Bawah (Scam)", f"Rp {lower_bound:,.0f}")
    c2.metric("Harga Rata-rata", f"Rp {mean_price:,.0f}")
    c3.metric("Batas Atas (Mahal)", f"Rp {upper_bound:,.0f}")

    # 2. Visualisasi Scatter Plot
    scatter = alt.Chart(df_chart).mark_circle(size=60).encode(
        x=alt.X('Harga_Int', title='Harga (IDR)', scale=alt.Scale(zero=False)),
        y=alt.Y('Terjual_Count', title='Jumlah Terjual (Unit)'),
        color=alt.Color('Status', scale=alt.Scale(
            domain=['Indikasi Scam / Rusak', 'Harga Wajar', 'Kemahalan'],
            range=['#D32F2F', '#388E3C', '#FBC02D']  # Merah, Hijau, Kuning
        )),
        tooltip=[
            alt.Tooltip('Judul', title='Judul Barang'),
            alt.Tooltip('Harga_Int', format=',.0f', title='Harga'),
            alt.Tooltip('Terjual_Count', title='Terjual'),
            alt.Tooltip('Toko', title='Toko'),
            alt.Tooltip('Status', title='Analisa')
        ]
    ).interactive().properties(
        height=400,
        title=f"Sebaran Harga (Wajar: Rp {lower_bound:,.0f} - {upper_bound:,.0f})"
    )

    st.altair_chart(scatter, use_container_width=True)
    
    st.info(f"""
    **Logika Deteksi Baru:**
    - Batas bawah dihitung berdasarkan **Rata-rata Pasar**.
    - Jika harga unit di bawah **Rp {lower_bound:,.0f}**, sistem menandainya sebagai **Indikasi Scam atau Rusak**.
    """)

def extract_variant(title):
    """
    Ekstrak varian model dari judul (Pro Max, Pro, Plus, atau Basic).
    """
    title_lower = str(title).lower()
    
    if "pro max" in title_lower:
        return "Pro Max"
    elif "pro" in title_lower:
        return "Pro"
    elif "plus" in title_lower:
        return "Plus"
    else:
        return "Basic"

def render_variant_breakdown(df):
    st.subheader("Analisis Detail: Varian & Kategori")
    st.caption("Breakdown harga berdasarkan varian (Pro/Max/Plus) dan asal barang (Inter/iBox/Cukai).")

    if df.empty:
        st.warning("Data kosong.")
        return

    # 1. Proses Data: Tambah kolom Varian
    # Kita menggunakan .copy() agar tidak merusak dataframe asli di cache
    df_chart = df.copy()
    df_chart['Varian'] = df_chart['Judul'].apply(extract_variant)

    # Urutan logis untuk chart
    varian_order = ["Pro Max", "Pro", "Plus", "Regular"]
    
    # 2. Chart Heatmap / Grouped Bar untuk Harga
    # Menampilkan Harga Rata-rata per Varian & Kategori
    
    base = alt.Chart(df_chart).encode(
        x=alt.X('Varian', sort=varian_order, axis=alt.Axis(title="Model Varian", labelAngle=0)),
        y=alt.Y('mean(Harga_Int):Q', title='Rata-rata Harga (IDR)', axis=alt.Axis(format=',.0f'))
    )

    # Chart Batang Berkelompok (Grouped Bar)
    chart = base.mark_bar().encode(
        x=alt.X('Varian', sort=varian_order, axis=None),
        color=alt.Color('Kategori', scale=alt.Scale(scheme='tableau10')),
        column=alt.Column('Kategori', header=alt.Header(titleOrient="bottom", labelOrient="bottom")),
        tooltip=[
            alt.Tooltip('Varian', title='Varian'),
            alt.Tooltip('Kategori', title='Region'),
            alt.Tooltip('mean(Harga_Int):Q', format=',.0f', title='Harga Rata-rata'),
            alt.Tooltip('count():Q', title='Jumlah Data')
        ]
    ).properties(
        width=120,
        height=300,
        title="Perbandingan Harga per Varian & Kategori"
    ).interactive()

    st.altair_chart(chart)

    # 3. Chart Distribusi Stok (Opsional, untuk melengkapi)
    st.caption("Proporsi Stok di Pasar")
    stock_chart = alt.Chart(df_chart).mark_bar().encode(
        y=alt.Y('Varian', sort=varian_order, title=None),
        x=alt.X('count():Q', title='Jumlah Barang'),
        color=alt.Color('Kategori', legend=alt.Legend(title="Kategori")),
        tooltip=['Varian', 'Kategori', 'count()']
    ).properties(height=200)
    
    st.altair_chart(stock_chart, use_container_width=True)
    
    #4. Filter Interaktif Sederhana (Tabel Mini)
    st.write("#### Cek Harga Spesifik")
    cols = st.columns(3)
    selected_varian = cols[0].selectbox("Pilih Varian", ["Semua"] + sorted(df_chart['Varian'].unique()))
    selected_cat = cols[1].selectbox("Pilih Kategori", ["Semua"] + sorted(df_chart['Kategori'].unique()))
    
    filtered_view = df_chart
    if selected_varian != "Semua":
        filtered_view = filtered_view[filtered_view['Varian'] == selected_varian]
    if selected_cat != "Semua":
        filtered_view = filtered_view[filtered_view['Kategori'] == selected_cat]
        
    avg_price = filtered_view['Harga_Int'].mean()
    min_price = filtered_view['Harga_Int'].min()
    max_price = filtered_view['Harga_Int'].max()
    
    if not filtered_view.empty:
        col_metric = st.columns(3)
        col_metric[0].metric("Harga Terendah", f"Rp {min_price:,.0f}")
        col_metric[1].metric("Harga Rata-rata", f"Rp {avg_price:,.0f}")
        col_metric[2].metric("Harga Tertinggi", f"Rp {max_price:,.0f}")
    else:
        st.info("Tidak ada data untuk kombinasi ini.")