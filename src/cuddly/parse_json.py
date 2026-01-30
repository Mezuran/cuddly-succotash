import pandas as pd
import re

def run():
    df = pd.read_csv('./data/iphone_tokopedia.csv')

    df['Judul_Cleaned'] = df['Judul'].str.replace(r'[|/]', ' ', regex=True)
    df['Judul_Cleaned'] = df['Judul_Cleaned'].str.replace(r'\s+', ' ', regex=True).str.strip()

    def check_consistency(row):
        model_norm = str(row['Model']).lower().replace(" ", "")
        title_norm = str(row['Judul']).lower().replace(" ", "")
        
        return model_norm in title_norm

    df_clean = df[df.apply(check_consistency, axis=1)].copy()

    def extract_storage(text):
        match = re.search(r'(\d+)\s?(GB|TB)', str(text), re.IGNORECASE)
        if match:
            return match.group(0).upper().replace(" ", "")
        return None

    df_clean['Storage'] = df_clean['Judul_Cleaned'].apply(extract_storage)

    print(f"Jumlah baris awal: {len(df)}")
    print(f"Jumlah baris setelah dibersihkan: {len(df_clean)}")

    df_clean.to_json('./data/iphone_tokopedia_cleaned.json', index=False, indent=4)

    print(df_clean[['Model', 'Judul_Cleaned', 'Storage']].head())