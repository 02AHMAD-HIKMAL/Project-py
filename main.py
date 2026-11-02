import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import serial


def inisialisasi_db():
    conn = sqlite3.connect("toko_kelontong.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            kode TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL
        )
    """)
    
    
    cursor.execute("SELECT COUNT(*) FROM produk")
    if cursor.fetchone()[0] == 0:
        data_awal = [
            ("A01", "Beras 5kg", 65000, 20),
            ("A02", "Minyak Goreng 1L", 18000, 30),
            ("A03", "Gula Pasir 1kg", 16000, 25),
            ("A04", "Telur 1kg", 28000, 15),
            ("A05", "Mie Instan (Dus)", 110000, 10)
        ]
        cursor.executemany("INSERT INTO produk VALUES (?, ?, ?, ?)", data_awal)
        conn.commit()
    conn.close()


class AplikasiKasir:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Kasir Pintar")
        self.root.geometry("950x620")
        
        inisialisasi_db()
        self.keranjang = []

        
        lbl_judul = tk.Label(root, text="TOKO MALLCELL - KASIR", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=10)
        lbl_judul.pack(fill=tk.X)

        frame_utama = tk.Frame(root, padx=10, pady=10)
        frame_utama.pack(fill=tk.BOTH, expand=True)

        
        frame_kiri = tk.Frame(frame_utama)
        frame_kiri.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(frame_kiri, text="Daftar Barang Tersedia", font=("Arial", 12, "bold")).pack(anchor="w")

        
        self.tree_produk = ttk.Treeview(frame_kiri, columns=("Kode", "Nama", "Harga", "Stok"), show="headings", height=12)
        self.tree_produk.heading("Kode", text="Kode")
        self.tree_produk.heading("Nama", text="Nama Barang")
        self.tree_produk.heading("Harga", text="Harga (Rp)")
        self.tree_produk.heading("Stok", text="Stok")
        self.tree_produk.column("Kode", width=60)
        self.tree_produk.column("Nama", width=150)
        self.tree_produk.column("Harga", width=90)
        self.tree_produk.column("Stok", width=50)
        self.tree_produk.pack(fill=tk.BOTH, expand=True, pady=5)

        
        btn_kelola_stok = tk.Button(frame_kiri, text="⚙️ Tambah / Kelola Stok Barang", bg="#e67e22", fg="white", font=("Arial", 10, "bold"), command=self.buka_jendela_stok)
        btn_kelola_stok.pack(fill=tk.X, pady=5)

       
        frame_input = tk.Frame(frame_kiri, pady=5)
        frame_input.pack(fill=tk.X)

        tk.Label(frame_input, text="Jumlah Beli:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_jumlah = tk.Entry(frame_input, width=10, font=("Arial", 11))
        self.entry_jumlah.pack(side=tk.LEFT, padx=(0, 10))

        btn_tambah = tk.Button(frame_input, text="Tambah ke Keranjang", bg="#27ae60", fg="white", font=("Arial", 10), command=self.tambah_ke_keranjang)
        btn_tambah.pack(side=tk.LEFT)

        
        frame_kanan = tk.Frame(frame_utama, width=350)
        frame_kanan.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        tk.Label(frame_kanan, text="Keranjang Belanja", font=("Arial", 12, "bold")).pack(anchor="w")

        
        self.tree_keranjang = ttk.Treeview(frame_kanan, columns=("Nama", "Qty", "Subtotal"), show="headings", height=10)
        self.tree_keranjang.heading("Nama", text="Item")
        self.tree_keranjang.heading("Qty", text="Qty")
        self.tree_keranjang.heading("Subtotal", text="Subtotal")
        self.tree_keranjang.column("Nama", width=140)
        self.tree_keranjang.column("Qty", width=40)
        self.tree_keranjang.column("Subtotal", width=90)
        self.tree_keranjang.pack(fill=tk.BOTH, pady=5)

        btn_hapus_item = tk.Button(frame_kanan, text="Hapus Item Terpilih", bg="#c0392b", fg="white", command=self.hapus_item_keranjang)
        btn_hapus_item.pack(fill=tk.X, pady=(0, 10))

        
        frame_bayar = tk.LabelFrame(frame_kanan, text="Pembayaran", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_bayar.pack(fill=tk.X, pady=5)

        tk.Label(frame_bayar, text="TOTAL:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_total_val = tk.Label(frame_bayar, text="Rp 0", font=("Arial", 12, "bold"), fg="#c0392b")
        self.lbl_total_val.grid(row=0, column=1, sticky="e")

        tk.Label(frame_bayar, text="Uang Tunai:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_bayar = tk.Entry(frame_bayar, font=("Arial", 11), width=12)
        self.entry_bayar.grid(row=1, column=1, sticky="e", pady=5)

        btn_proses = tk.Button(frame_bayar, text="Proses & Cetak Struk (BT)", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=self.proses_transaksi)
        btn_proses.grid(row=2, column=0, columnspan=2, sticky="we", pady=10)

        self.muat_data_produk()

    def muat_data_produk(self):
        for item in self.tree_produk.get_children():
            self.tree_produk.delete(item)
            
        conn = sqlite3.connect("toko_kelontong.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produk")
        for baris in cursor.fetchall():
            self.tree_produk.insert("", tk.END, values=(baris[0], baris[1], f"Rp {baris[2]:,}", baris[3]))
        conn.close()

    def buka_jendela_stok(self):
        """Membuka jendela baru untuk menambah stok atau produk baru"""
        jendela_stok = tk.Toplevel(self.root)
        jendela_stok.title("Kelola Stok & Barang")
        jendela_stok.geometry("400x380")
        jendela_stok.grab_set() # Fokus ke jendela ini

        tk.Label(jendela_stok, text="Tambah / Perbarui Stok Barang", font=("Arial", 12, "bold"), pady=10).pack()

        form = tk.Frame(jendela_stok, padx=15, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Kode Barang (Unik, misal: A06):").pack(anchor="w")
        e_kode = tk.Entry(form, font=("Arial", 11), width=25)
        e_kode.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Nama Barang:").pack(anchor="w")
        e_nama = tk.Entry(form, font=("Arial", 11), width=25)
        e_nama.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Harga Satuan (Rp):").pack(anchor="w")
        e_harga = tk.Entry(form, font=("Arial", 11), width=25)
        e_harga.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Jumlah Stok yang Ditambahkan/Diset:").pack(anchor="w")
        e_stok = tk.Entry(form, font=("Arial", 11), width=25)
        e_stok.pack(fill=tk.X, pady=(0, 15))

        def simpan_stok_db():
            kode = e_kode.get().strip().upper()
            nama = e_nama.get().strip()
            harga_str = e_harga.get().strip()
            stok_str = e_stok.get().strip()

            if not kode or not nama or not harga_str or not stok_str:
                messagebox.showerror("Error", "Semua kolom harus diisi!", parent=jendela_stok)
                return

            if not harga_str.isdigit() or not stok_str.isdigit():
                messagebox.showerror("Error", "Harga dan stok harus berupa angka!", parent=jendela_stok)
                return

            harga = int(harga_str)
            stok = int(stok_str)

            conn = sqlite3.connect("toko_kelontong.db")
            cursor = conn.cursor()

            
            cursor.execute("SELECT stok FROM produk WHERE kode = ?", (kode,))
            hasil = cursor.fetchone()

            if hasil:
                
                cursor.execute("UPDATE produk SET nama = ?, harga = ?, stok = stok + ? WHERE kode = ?", (nama, harga, stok, kode))
                pesan = f"Stok barang {nama} berhasil ditambahkan sebanyak {stok}!"
            else:
                
                cursor.execute("INSERT INTO produk VALUES (?, ?, ?, ?)", (kode, nama, harga, stok))
                pesan = f"Produk baru {nama} berhasil ditambahkan!"

            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", pesan, parent=jendela_stok)
            self.muat_data_produk()
            jendela_stok.destroy()

        btn_simpan = tk.Button(form, text="Simpan / Tambah Stok", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=simpan_stok_db)
        btn_simpan.pack(fill=tk.X)

    