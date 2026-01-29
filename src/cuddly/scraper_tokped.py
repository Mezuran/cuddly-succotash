import time
import random
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

MAX_DATA = 100
list_iphone = [
    "iPhone 11"
    , "iPhone 11 Pro", "iPhone 11 Pro Max",
    "iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max"
]

jenis_kondisi = {
    "Inter": "second inter",
    "iBox": "second resmi ibox",
    "Cukai": "second all operator imei terdaftar" 
}

# konfig selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
data_hasil = []

def scroll_to_bottom(driver):
    for _ in range(8): 
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(1.5)

# loop dapetin data
print(f"Mulai scraping tokped (Target: Max {MAX_DATA} data per kategori)")

for model in list_iphone:
    for tipe, keyword in jenis_kondisi.items():
        query = f"{model} {keyword}"
        print(f"\nSedang mencari: {query}")
        
        encoded_query = query.replace(" ", "%20")
        url = f"https://www.tokopedia.com/search?st=product&q={encoded_query}&navsource=home"
        
        driver.get(url)
        time.sleep(3)
        scroll_to_bottom(driver)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = soup.select("div.css-llwpbs")
        if len(products) < 10:
            products = soup.select("div.css-5wh65g")

        count = 0

        for product in products:
            if count >= MAX_DATA:
                break 

            # Ambil Judul
            nama_el = product.select_one("span[class*='tnoqZhn89']")
            nama_produk = nama_el.get_text() if nama_el else "-"

            # Ambil Harga
            harga_el = product.select_one("div[class*='urMOIDHH']")
            harga = harga_el.get_text() if harga_el else "0"

            # Ambil Toko
            toko_el = product.select_one("span[class*='si3CNdiG8AR']")
            toko = toko_el.get_text() if toko_el else "-"

            # Ambil Terjual
            terjual_el = product.select_one("span[class*='u6SfjDD2WiBl']")
            terjual = terjual_el.get_text() if terjual_el else "0 terjual"

            # Ambil Lokasi (Manual)
            lokasi = "-" 
            kota_keywords = [
                "Jakarta", "Bandung", "Surabaya", "Tangerang", "Bekasi", 
                "Depok", "Bogor", "Semarang", "Yogyakarta", "Sleman", 
                "Banten", "Jawa", "Medan", "Batam", "Makassar", "Malang", 
                "Solo", "Denpasar", "Kab.", "Kota ", "Pekanbaru", "Palembang",
                "Samarinda", "Balikpapan", "Cimahi", "Tasikmalaya"
            ]
            
            # Cari semua span dalam produk
            all_spans = product.find_all("span")
            found_loc = False
            
            # Loop terbalik (reversed)
            for span in reversed(all_spans):
                txt = span.get_text().strip()
                # Validasi string
                if (any(k in txt for k in kota_keywords) and 
                    len(txt) < 35 and 
                    "Rp" not in txt and 
                    "Terjual" not in txt and
                    "rating" not in txt.lower()):
                    
                    lokasi = txt
                    found_loc = True
                    break

            # Filter dan Simpan
            if "iphone" in nama_produk.lower():
                data_hasil.append({
                    "Pencarian": query,
                    "Model": model,
                    "Kategori": tipe,
                    "Judul": nama_produk,
                    "Harga": harga,
                    "Lokasi": lokasi,
                    "Toko": toko,
                    "Terjual": terjual
                })
                count += 1

        print(f"    Ada {count} data")

        time.sleep(random.uniform(2, 4))

driver.quit()

df = pd.DataFrame(data_hasil)

# harga yang int
df['Harga_Int'] = df['Harga'].str.replace('Rp', '').str.replace('.', '').astype(float)

# save data
foldername = "data"
filename = "iphone_tokopedia.csv"

if not os.path.exists(foldername):
    os.makedirs(foldername)

full_path = os.path.join(foldername, filename)
df.to_csv(full_path, index=False)

print(f"\nDone, Data : {len(df)}")