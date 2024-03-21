import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import pymongo

def makaleleri_tara(sorgu, sayfa_sayisi):
    # Google Scholar'da belirli bir sorgu ile arama yaparak makaleleri tarar
    veri_listesi = []
    sayfa = 0
    while sayfa < sayfa_sayisi:
        url = f"https://scholar.google.com/scholar?start={sayfa*10}&q={sorgu}&hl=tr&as_sdt=0,5"
        cevap = requests.get(url)
        soup = BeautifulSoup(cevap.text, "html.parser")
        sonuclar = soup.find_all("div", class_="gs_r gs_or gs_scl")

        for sonuc in sonuclar:
            baslik = sonuc.find("h3", class_="gs_rt").text
            link = sonuc.find("a")["href"]
            yayin_bilgisi = sonuc.find("div", class_="gs_a").text

            yazarlar = ""
            yil = ""
            for bilgi in yayin_bilgisi.split(" - "):
                if "Yayın" in bilgi:
                    yil = bilgi.strip()
                elif not bilgi.startswith("[") and not bilgi.endswith("...]"):
                    yazarlar += bilgi + ", "
            
            yazarlar = yazarlar.rstrip(", ")

            veri_listesi.append({"Yayın Adı": baslik, "Yazar Adı ve Yayın Yılı": yazarlar + " - " + yil, "URL": link})

        sayfa += 1

    return veri_listesi

def excel_aktar(veri_listesi, dosya_adi):
    # Veri listesini Excel dosyasına aktarır
    df = pd.DataFrame(veri_listesi)
    df.to_excel(dosya_adi, index=False)

def klasor_sec():
    # Kullanıcıya klasör seçme penceresi açar
    klasor_yolu = filedialog.askdirectory()
    entry_klasor.delete(0, tk.END)
    entry_klasor.insert(tk.END, klasor_yolu)

def makaleleri_tara_aksiyon():
    # Makaleleri tara butonuna basıldığında çalışacak işlemleri gerçekleştirir
    sorgu = entry_sorgu.get()
    sayfa_sayisi = int(entry_sayfa.get())

    veri_listesi = makaleleri_tara(sorgu, sayfa_sayisi)

    klasor_yolu = entry_klasor.get()
    if klasor_yolu:
        dosya_adi = f"{klasor_yolu}/scholar_verileri.xlsx"
    else:
        dosya_adi = "scholar_verileri.xlsx"

    excel_aktar(veri_listesi, dosya_adi)

    # MongoDB'ye veri kaydı
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["PythonDatabase"]
    collection = db["scholar_veriler"]

    for veri in veri_listesi:
        collection.insert_one(veri)

    label_durum.config(text="Veri çekme tamamlandı. \nVeriler scholar_verileri.xlsx dosyasına ve \nMongoDB veritabanına kaydedildi.")

# Ana pencere oluştur
pencere = tk.Tk()
pencere.title("Google Scholar Veri Çekme")
pencere.geometry("500x300")

# Giriş alanları ve etiketleri
frame_giris = tk.Frame(pencere)
frame_giris.pack(pady=10)

etiket_sorgu = tk.Label(frame_giris, text="Makale Başlığı veya Anahtar Kelime:")
etiket_sorgu.grid(row=0, column=0, padx=5, pady=5)
entry_sorgu = tk.Entry(frame_giris, width=40)
entry_sorgu.grid(row=0, column=1, padx=5, pady=5)

etiket_sayfa = tk.Label(frame_giris, text="Sayfa Sayısı:")
etiket_sayfa.grid(row=1, column=0, padx=5, pady=5)
entry_sayfa = tk.Entry(frame_giris, width=40)
entry_sayfa.grid(row=1, column=1, padx=5, pady=5)

etiket_klasor = tk.Label(frame_giris, text="Çıkış Klasörü (isteğe bağlı):")
etiket_klasor.grid(row=2, column=0, padx=5, pady=5)
entry_klasor = tk.Entry(frame_giris, width=40)
entry_klasor.grid(row=2, column=1, padx=5, pady=5)

# Klasör seçme ve veri çekme butonları
frame_butonlar = tk.Frame(pencere)
frame_butonlar.pack(pady=10)

button_klasor = tk.Button(frame_butonlar, text="Klasör Seç", command=klasor_sec, padx=10, pady=5)
button_klasor.pack(side=tk.LEFT, padx=10)

button_veri_cek = tk.Button(frame_butonlar, text="Veri Çek", command=makaleleri_tara_aksiyon, padx=10, pady=5)
button_veri_cek.pack(side=tk.LEFT, padx=10)

# Durum etiketi
label_durum = tk.Label(pencere, text="", font=("Arial", 12))
label_durum.pack(pady=10)

# Ana pencere döngüsünü çalıştır
pencere.mainloop()
