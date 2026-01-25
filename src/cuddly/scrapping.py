import pandas as pd
import re

def run():
    # 1. Load Data
    df = pd.read_csv('./data/iphone_tokopedia.csv')

    # --- TAHAP 1: MEMBERSIHKAN KARAKTER ---
    # Mengganti '/' dan '|' dengan spasi agar kata-kata tidak menempel
    df['Judul_Cleaned'] = df['Judul'].str.replace(r'[|/]', ' ', regex=True)
    # Menghapus spasi berlebih yang terbentuk akibat penghapusan di atas
    df['Judul_Cleaned'] = df['Judul_Cleaned'].str.replace(r'\s+', ' ', regex=True).str.strip()


    # --- TAHAP 2: FILTER DATA SAMPAH (KONSISTENSI) ---
    # Logika: Jika nama 'Model' tidak ada di dalam 'Judul', maka itu data sampah/salah kategori.
    def check_consistency(row):
        # Normalisasi: ubah ke huruf kecil dan hilangkan spasi untuk pencarian yang lebih akurat
        # Contoh: "iPhone 11 Pro" akan cocok dengan "iPhone 11Pro" atau "IPHONE 11 PRO"
        model_norm = str(row['Model']).lower().replace(" ", "")
        title_norm = str(row['Judul']).lower().replace(" ", "")
        
        return model_norm in title_norm

    # Terapkan filter (hanya simpan yang True)
    df_clean = df[df.apply(check_consistency, axis=1)].copy()


    # --- TAHAP 3: TAMBAH COLUMN STORAGE ---
    def extract_storage(text):
        # Regex untuk mencari angka yang diikuti GB atau TB (case insensitive)
        # Contoh menangkap: "64gb", "128 GB", "1 TB"
        match = re.search(r'(\d+)\s?(GB|TB)', str(text), re.IGNORECASE)
        if match:
            # Mengembalikan format standar (misal: "128GB")
            return match.group(0).upper().replace(" ", "")
        return None

    df_clean['Storage'] = df_clean['Judul_Cleaned'].apply(extract_storage)


    # --- HASIL ---
    # Menampilkan info data sebelum dan sesudah
    print(f"Jumlah baris awal: {len(df)}")
    print(f"Jumlah baris setelah dibersihkan: {len(df_clean)}")

    # Simpan ke CSV baru
    df_clean.to_csv('./data/iphone_tokopedia_cleaned.csv', index=False)

    # Preview data
    print(df_clean[['Model', 'Judul_Cleaned', 'Storage']].head())