import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# --- VERİTABANI BAĞLANTISI ---
def db_baglan():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",      # XAMPP varsayılan kullanıcı adı
            password="",      # XAMPP varsayılan şifre (boştur)
            database="yzp"    # Kendi veritabanı adın
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Bağlantı Hatası", f"Veritabanına ulaşılamadı!\nXAMPP MySQL açık mı?\nHata: {err}")
        return None

# --- ÖĞRENCİ EKLEME MODÜLÜ ---
def ogrenci_ekle_penceresi():
    pencere = tk.Toplevel()
    pencere.title("Yeni Öğrenci Kaydı")
    pencere.geometry("350x300")
    
    # Arayüz Elemanları
    tk.Label(pencere, text="Öğrenci No:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_ogrno = tk.Entry(pencere)
    entry_ogrno.grid(row=0, column=1)

    tk.Label(pencere, text="Adı:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_ad = tk.Entry(pencere)
    entry_ad.grid(row=1, column=1)

    tk.Label(pencere, text="Soyadı:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_soyad = tk.Entry(pencere)
    entry_soyad.grid(row=2, column=1)

    # Bölümleri Veritabanından Çekip Combobox'a (Açılır Liste) Ekleme
    tk.Label(pencere, text="Bölüm:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    combo_bolum = ttk.Combobox(pencere, state="readonly")
    combo_bolum.grid(row=3, column=1)
    
    bolumler_dict = {}
    conn = db_baglan()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT bolum_id, bolum_adi FROM Bolumler")
        for b_id, b_adi in cursor.fetchall():
            bolumler_dict[b_adi] = b_id
            combo_bolum['values'] = tuple(bolumler_dict.keys())
        conn.close()

    # Kayıt Fonksiyonu
    def kaydet():
        ogrno = entry_ogrno.get()
        ad = entry_ad.get()
        soyad = entry_soyad.get()
        secilen_bolum = combo_bolum.get()

        if not (ogrno and ad and soyad and secilen_bolum):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        bolum_id = bolumler_dict[secilen_bolum]

        try:
            conn = db_baglan()
            cursor = conn.cursor()
            sql = "INSERT INTO Ogrenciler (ogrNO, ad, soyadi, bolum_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ogrno, ad, soyad, bolum_id))
            conn.commit()
            messagebox.showinfo("Başarılı", "Öğrenci sisteme başarıyla eklendi!")
            pencere.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt eklenemedi:\n{e}")
        finally:
            if conn: conn.close()

    tk.Button(pencere, text="Sisteme Kaydet", command=kaydet, bg="green", fg="white").grid(row=4, column=1, pady=20)


# --- NOT GİRİŞİ MODÜLÜ ---
def not_girisi_penceresi():
    pencere = tk.Toplevel()
    pencere.title("Sınav Notu Girişi")
    pencere.geometry("350x250")

    tk.Label(pencere, text="Öğrenci No:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_ogrno = tk.Entry(pencere)
    entry_ogrno.grid(row=0, column=1)

    tk.Label(pencere, text="Ders Kodu (Örn: HKK101):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_ders = tk.Entry(pencere)
    entry_ders.grid(row=1, column=1)

    tk.Label(pencere, text="Vize Notu:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_vize = tk.Entry(pencere)
    entry_vize.grid(row=2, column=1)

    tk.Label(pencere, text="Final Notu:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    entry_final = tk.Entry(pencere)
    entry_final.grid(row=3, column=1)

    def not_guncelle():
        ogrno = entry_ogrno.get()
        ders_kodu = entry_ders.get()
        vize = entry_vize.get()
        final = entry_final.get()

        try:
            conn = db_baglan()
            cursor = conn.cursor()
            
            # İç içe geçmiş tabloları JOIN ile bulup güncelliyoruz
            sql = """
                UPDATE Ogrenci_Ders_Kayit odk
                JOIN Ogrenciler o ON odk.ogrenci_id = o.ogrenci_id
                JOIN Acilan_Dersler ad ON odk.acilan_ders_id = ad.acilan_ders_id
                JOIN Dersler d ON ad.ders_id = d.ders_id
                SET odk.vize = %s, odk.final = %s
                WHERE o.ogrNO = %s AND d.ders_kodu = %s
            """
            cursor.execute(sql, (vize, final, ogrno, ders_kodu))
            
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Başarılı", "Notlar sisteme işlendi!")
                pencere.destroy()
            else:
                messagebox.showwarning("Bulunamadı", "Bu öğrenci numarasına ve ders koduna ait aktif bir kayıt bulunamadı.")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Not güncellenemedi:\n{e}")
        finally:
            if conn: conn.close()

    tk.Button(pencere, text="Notları İşle", command=not_guncelle, bg="blue", fg="white").grid(row=4, column=1, pady=20)


# --- ANA MENÜ ---
root = tk.Tk()
root.title("Üniversite Öğrenci Otomasyonu v1.0")
root.geometry("400x300")

tk.Label(root, text="Yönetim Paneline Hoş Geldiniz", font=("Arial", 14, "bold")).pack(pady=30)

btn_ogrenci = tk.Button(root, text="Yeni Öğrenci Ekle", font=("Arial", 12), width=20, command=ogrenci_ekle_penceresi)
btn_ogrenci.pack(pady=10)

btn_not = tk.Button(root, text="Sınav Notu Gir", font=("Arial", 12), width=20, command=not_girisi_penceresi)
btn_not.pack(pady=10)

root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def db_baglan():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="yzp"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Bağlantı Hatası", f"Veritabanı bağlantısı sağlanamadı: {err}")
        return None

def veri_listeleme_penceresi():
    pencere = tk.Toplevel()
    pencere.title("Öğrenci Bilgi Gezgini")
    pencere.geometry("900x500")

    # Tablo kolonlarını tanımlıyoruz
    columns = ('no', 'ad', 'soyad', 'bolum', 'vize', 'final', 'ort')
    tree = ttk.Treeview(pencere, columns=columns, show='headings')

    # Başlıkları oluşturuyoruz
    tree.heading('no', text='Öğrenci No')
    tree.heading('ad', text='Ad')
    tree.heading('soyad', text='Soyad')
    tree.heading('bolum', text='Bölüm')
    tree.heading('vize', text='Vize')
    tree.heading('final', text='Final')
    tree.heading('ort', text='Ortalama')

    # Kolon genişliklerini ve hizalamaları ayarlıyoruz
    tree.column('no', width=100, anchor="center")
    tree.column('ort', width=100, anchor="center")

    # Veritabanından ilişkili verileri çekiyoruz
    conn = db_baglan()
    if conn:
        cursor = conn.cursor()
        # 3 tabloyu JOIN ile birleştirerek tüm bilgiyi tek seferde alıyoruz
        sorgu = """
            SELECT o.ogrNO, o.ad, o.soyadi, b.bolum_adi, odk.vize, odk.final, odk.ortalama
            FROM Ogrenciler o
            LEFT JOIN Bolumler b ON o.bolum_id = b.bolum_id
            LEFT JOIN Ogrenci_Ders_Kayit odk ON o.ogrenci_id = odk.ogrenci_id
        """
        cursor.execute(sorgu)
        for satir in cursor.fetchall():
            tree.insert('', tk.END, values=satir)
        conn.close()

    # Tabloyu ekrana yerleştirme ve Scrollbar ekleme
    tree.pack(side=tk.LEFT, expand=True, fill='both', padx=10, pady=10)
    
    sb = ttk.Scrollbar(pencere, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

# Ana menüye 'Verileri Listele' butonu ekleyerek bu fonksiyonu çağırabilirsin.
