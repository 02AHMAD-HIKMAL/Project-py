from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import serial


def inisialisasi_db():
    conn = sqlite3.connect("toko_mallcell.db")
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
            ("A05", "Mie Instan ( 1 Dus)", 110000, 10)
        ]
        cursor.executemany("INSERT INTO produk VALUES (?, ?, ?, ?)", data_awal)
        conn.commit()
    conn.close()


class AplikasiKasirModern:
    def __init__(self, root):
        self.root = root
        self.root.title("Kasir Pintar")
        self.root.geometry("1024x680")
        self.root.configure(bg="#f8f9fa")
        
        inisialisasi_db()
        self.keranjang = []

        
        self.warna_bg_utama = "#f8f9fa"
        self.warna_header = "#1e293b"      
        self.warna_primary = "#2563eb"     
        self.warna_success = "#16a34a"     
        self.warna_danger = "#dc2626"      
        self.warna_warning = "#d97706"     

        
        header_frame = tk.Frame(root, bg=self.warna_header, pady=15)
        header_frame.pack(fill=tk.X)


        lbl_title = tk.Label(header_frame, text="TOKO MALLCELL", font=("Segoe UI", 18, "bold"), bg=self.warna_header, fg="white")
        lbl_title.pack()
        lbl_subtitle = tk.Label(header_frame, text="Kasir Pintar", font=("Segoe UI", 10), bg=self.warna_header, fg="#94a3b8")
        lbl_subtitle.pack()

        
        main_container = tk.Frame(root, bg=self.warna_bg_utama, padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        
        left_frame = tk.Frame(main_container, bg=self.warna_bg_utama)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        lbl_katalog = tk.Label(left_frame, text="Katalog Produk", font=("Segoe UI", 12, "bold"), bg=self.warna_bg_utama, fg="#334155")
        lbl_katalog.pack(anchor="w", pady=(0, 5))


        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1e293b")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26, background="white", fieldbackground="white")

        tree_scroll = ttk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        self.tree_produk = ttk.Treeview(left_frame, columns=("Kode", "Nama", "Harga", "Stok"), show="headings", yscrollcommand=tree_scroll.set, height=14)
        self.tree_produk.heading("Kode", text="KODE")
        self.tree_produk.heading("Nama", text="NAMA BARANG")
        self.tree_produk.heading("Harga", text="HARGA (RP)")
        self.tree_produk.heading("Stok", text="STOK")
        
        self.tree_produk.column("Kode", width=70, anchor="center")
        self.tree_produk.column("Nama", width=180, anchor="w")
        self.tree_produk.column("Harga", width=110, anchor="e")
        self.tree_produk.column("Stok", width=60, anchor="center")
        self.tree_produk.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree_produk.yview)

        action_left_frame = tk.Frame(left_frame, bg=self.warna_bg_utama, pady=10)
        action_left_frame.pack(fill=tk.X)

        btn_kelola_stok = tk.Button(action_left_frame, text="⚙️ Kelola / Tambah Stok", bg=self.warna_warning, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=6, cursor="hand2", command=self.buka_jendela_stok)
        btn_kelola_stok.pack(side=tk.LEFT)

        qty_frame = tk.Frame(action_left_frame, bg=self.warna_bg_utama)
        qty_frame.pack(side=tk.RIGHT)

        tk.Label(qty_frame, text="Qty:", font=("Segoe UI", 10, "bold"), bg=self.warna_bg_utama).pack(side=tk.LEFT, padx=5)
        self.entry_jumlah = tk.Entry(qty_frame, font=("Segoe UI", 11), width=6, justify="center")
        self.entry_jumlah.pack(side=tk.LEFT, padx=5)
        self.entry_jumlah.insert(0, "1")

        btn_tambah = tk.Button(qty_frame, text="+ Masukkan", bg=self.warna_success, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=6, cursor="hand2", command=self.tambah_ke_keranjang)
        btn_tambah.pack(side=tk.LEFT, padx=5)

        right_frame = tk.Frame(main_container, bg="white", padx=15, pady=15, relief="solid", bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, ipadx=10)

        lbl_keranjang = tk.Label(right_frame, text="🛒 Keranjang Belanja", font=("Segoe UI", 12, "bold"), bg="white", fg="#1e293b")
        lbl_keranjang.pack(anchor="w", pady=(0, 5))

        self.tree_keranjang = ttk.Treeview(right_frame, columns=("Nama", "Qty", "Subtotal"), show="headings", height=10)
        self.tree_keranjang.heading("Nama", text="ITEM")
        self.tree_keranjang.heading("Qty", text="QTY")
        self.tree_keranjang.heading("Subtotal", text="SUBTOTAL")
        
        self.tree_keranjang.column("Nama", width=140, anchor="w")
        self.tree_keranjang.column("Qty", width=40, anchor="center")
        self.tree_keranjang.column("Subtotal", width=100, anchor="e")
        self.tree_keranjang.pack(fill=tk.BOTH, pady=5)

        btn_hapus_item = tk.Button(right_frame, text="Hapus Item Terpilih", bg=self.warna_danger, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", pady=4, cursor="hand2", command=self.hapus_item_keranjang)
        btn_hapus_item.pack(fill=tk.X, pady=(0, 10))



        # Panel Pembayaran Modern
        pay_panel = tk.Frame(right_frame, bg="#f1f5f9", padx=12, pady=12)
        pay_panel.pack(fill=tk.X, pady=5)

        lbl_tot_text = tk.Label(pay_panel, text="TOTAL TAGIHAN:", font=("Segoe UI", 10, "bold"), bg="#f1f5f9", fg="#475569")
        lbl_tot_text.grid(row=0, column=0, sticky="w")
        
        self.lbl_total_val = tk.Label(pay_panel, text="Rp 0", font=("Segoe UI", 14, "bold"), bg="#f1f5f9", fg=self.warna_danger)
        self.lbl_total_val.grid(row=0, column=1, sticky="e")

        lbl_bayar_text = tk.Label(pay_panel, text="Uang Tunai (Rp):", font=("Segoe UI", 10), bg="#f1f5f9", fg="#475569")
        lbl_bayar_text.grid(row=1, column=0, sticky="w", pady=(10, 0))

        self.entry_bayar = tk.Entry(pay_panel, font=("Segoe UI", 12), width=12, justify="right")
        self.entry_bayar.grid(row=1, column=1, sticky="e", pady=(10, 0))

        btn_proses = tk.Button(right_frame, text="PROSES & CETAK STRUK (BLUETOOTH)", bg=self.warna_primary, fg="white", font=("Segoe UI", 11, "bold"), relief="flat", pady=10, cursor="hand2", command=self.proses_transaksi)
        btn_proses.pack(fill=tk.X, pady=(15, 0))

        self.muat_data_produk()


    def muat_data_produk(self):
        for item in self.tree_produk.get_children():
            self.tree_produk.delete(item)
            
        conn = sqlite3.connect("toko_mallcell.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produk")
        for baris in cursor.fetchall():
            self.tree_produk.insert("", tk.END, values=(baris[0], baris[1], f"Rp {baris[2]:,}", baris[3]))
        conn.close()


    def buka_jendela_stok(self):
        jendela_stok = tk.Toplevel(self.root)
        jendela_stok.title("Manajemen Stok - TOKO MALLCELL")
        jendela_stok.geometry("420x420")
        jendela_stok.configure(bg="white")
        jendela_stok.grab_set()

        tk.Label(jendela_stok, text="Kelola Produk & Stok Barang", font=("Segoe UI", 13, "bold"), bg="white", fg="#1e293b", pady=15).pack()

        form = tk.Frame(jendela_stok, bg="white", padx=20)
        form.pack(fill=tk.BOTH, expand=True)


        tk.Label(form, text="Kode Barang (Unik):", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        e_kode = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1)
        e_kode.pack(fill=tk.X, pady=(2, 10), ipady=3)


        tk.Label(form, text="Nama Barang:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        e_nama = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1)
        e_nama.pack(fill=tk.X, pady=(2, 10), ipady=3)


        tk.Label(form, text="Harga Satuan (Rp):", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        e_harga = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1)
        e_harga.pack(fill=tk.X, pady=(2, 10), ipady=3)


        tk.Label(form, text="Jumlah Stok Baru / Tambahan:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w")
        e_stok = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1)
        e_stok.pack(fill=tk.X, pady=(2, 15), ipady=3)



        def simpan_stok_db():
            kode = e_kode.get().strip().upper()
            nama = e_nama.get().strip()
            harga_str = e_harga.get().strip()
            stok_str = e_stok.get().strip()

            if not kode or not nama or not harga_str or not stok_str:
                messagebox.showerror("Error", "Semua kolom wajib diisi!", parent=jendela_stok)
                return

            if not harga_str.isdigit() or not stok_str.isdigit():
                messagebox.showerror("Error", "Harga dan stok harus berupa angka valid!", parent=jendela_stok)
                return

            conn = sqlite3.connect("toko_mallcell.db")
            cursor = conn.cursor()
            cursor.execute("SELECT stok FROM produk WHERE kode = ?", (kode,))
            hasil = cursor.fetchone()

            if hasil:
                cursor.execute("UPDATE produk SET nama = ?, harga = ?, stok = stok + ? WHERE kode = ?", (nama, int(harga_str), int(stok_str), kode))
                pesan = f"Stok barang {nama} berhasil diperbarui!"
            else:
                cursor.execute("INSERT INTO produk VALUES (?, ?, ?, ?)", (kode, nama, int(harga_str), int(stok_str)))
                pesan = f"Produk baru {nama} berhasil ditambahkan!"

            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", pesan, parent=jendela_stok)
            self.muat_data_produk()
            jendela_stok.destroy()

        btn_simpan = tk.Button(form, text="Simpan Data", bg=self.warna_success, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=8, cursor="hand2", command=simpan_stok_db)
        btn_simpan.pack(fill=tk.X, pady=5)


    def tambah_ke_keranjang(self):
        selected_item = self.tree_produk.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Silakan pilih produk dari tabel terlebih dahulu!")
            return

        qty_str = self.entry_jumlah.get()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showerror("Error", "Jumlah beli harus berupa angka lebih besar dari 0!")
            return

        qty = int(qty_str)
        item_data = self.tree_produk.item(selected_item)
        kode = item_data['values'][0]
        nama = item_data['values'][1]
        harga = int(item_data['values'][2].replace("Rp ", "").replace(",", ""))
        stok_tersedia = int(item_data['values'][3])

        if qty > stok_tersedia:
            messagebox.showerror("Stok Kurang", f"Stok tidak mencukupi! Sisa stok saat ini: {stok_tersedia}")
            return

        for item in self.keranjang:
            if item['kode'] == kode:
                if item['jumlah'] + qty > stok_tersedia:
                    messagebox.showerror("Stok Kurang", "Total kuantitas melebihi sisa stok!")
                    return
                item['jumlah'] += qty
                item['subtotal'] = item['jumlah'] * harga
                self.update_tampilan_keranjang()
                return

        self.keranjang.append({
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "jumlah": qty,
            "subtotal": harga * qty
        })
        self.update_tampilan_keranjang()

    def hapus_item_keranjang(self):
        selected_item = self.tree_keranjang.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih item di keranjang yang ingin dihapus!")
            return
        index = self.tree_keranjang.index(selected_item)
        del self.keranjang[index]
        self.update_tampilan_keranjang()


    def update_tampilan_keranjang(self):
        for item in self.tree_keranjang.get_children():
            self.tree_keranjang.delete(item)
            
        total_belanja = 0
        for item in self.keranjang:
            self.tree_keranjang.insert("", tk.END, values=(item['nama'], item['jumlah'], f"Rp {item['subtotal']:,}"))
            total_belanja += item['subtotal']
            
        self.lbl_total_val.config(text=f"Rp {total_belanja:,}")


    def hitung_total_belanja(self):
        return sum(item['subtotal'] for item in self.keranjang)


    def proses_transaksi(self):
        if not self.keranjang:
            messagebox.showwarning("Keranjang Kosong", "Belum ada produk yang dimasukkan ke keranjang!")
            return

        bayar_str = self.entry_bayar.get()
        if not bayar_str.isdigit():
            messagebox.showerror("Error Pembayaran", "Masukkan nominal uang tunai dengan benar!")
            return

        bayar = int(bayar_str)
        total_belanja = self.hitung_total_belanja()

        if bayar < total_belanja:
            messagebox.showerror("Uang Kurang", f"Uang tunai kurang sebesar Rp {total_belanja - bayar:,}!")
            return

        kembalian = bayar - total_belanja

        conn = sqlite3.connect("toko_mallcell.db")
        cursor = conn.cursor()
        for item in self.keranjang:
            cursor.execute("UPDATE produk SET stok = stok - ? WHERE kode = ?", (item['jumlah'], item['kode']))
        conn.commit()
        conn.close()


        # Cetak Struk Bluetooth
        self.cetak_ke_bluetooth_thermal(total_belanja, bayar, kembalian)

        messagebox.showinfo("Transaksi Berhasil", f"Pembayaran Berhasil!\nUang Kembalian: Rp {kembalian:,}")
        
        self.keranjang.clear()
        self.update_tampilan_keranjang()
        self.entry_bayar.delete(0, tk.END)
        self.muat_data_produk()

    def cetak_ke_bluetooth_thermal(self, total_belanja, bayar, kembalian):
        PORT_BLUETOOTH = "COM7"  
        BAUD_RATE = 9600

        try:
            printer = serial.Serial(PORT_BLUETOOTH, BAUD_RATE, timeout=1)
            
            INIT = b'\x1b\x40'
            ALIGN_CENTER = b'\x1b\x61\x01'
            ALIGN_LEFT = b'\x1b\x61\x00'
            BOLD_ON = b'\x1b\x45\x01'
            BOLD_OFF = b'\x1b\x45\x00'
            CUT_PAPER = b'\x1d\x56\x42\x00'

            waktu_sekarang = datetime.now().strftime("%d/%m/%Y %H:%M")

            struk_data = bytearray()
            struk_data.extend(INIT)
            
            struk_data.extend(ALIGN_CENTER)
            struk_data.extend(BOLD_ON)
            struk_data.extend("TOKO MALLCELL\n".encode('utf-8'))
            struk_data.extend(BOLD_OFF)
            struk_data.extend("Jl. Raya Kediri\n".encode('utf-8'))
            struk_data.extend(f"Waktu: {waktu_sekarang}\n".encode('utf-8'))
            struk_data.extend(("-" * 32 + "\n").encode('utf-8'))
            
            struk_data.extend(ALIGN_LEFT)
            for item in self.keranjang:
                struk_data.extend(f"{item['nama'][:32]}\n".encode('utf-8'))
                struk_data.extend(f"  {item['jumlah']} x {item['harga']:,} = {item['subtotal']:,}\n".encode('utf-8'))
            
            
            struk_data.extend(("-" * 32 + "\n").encode('utf-8'))
            struk_data.extend(BOLD_ON)
            struk_data.extend(f"TOTAL   : Rp {total_belanja:,}\n".encode('utf-8'))
            struk_data.extend(f"BAYAR   : Rp {bayar:,}\n".encode('utf-8'))
            struk_data.extend(f"KEMBALI : Rp {kembalian:,}\n".encode('utf-8'))
            struk_data.extend(BOLD_OFF)
            
            
            struk_data.extend(("-" * 32 + "\n").encode('utf-8'))
            struk_data.extend(ALIGN_CENTER)
            struk_data.extend("Terima Kasih Atas Kunjungan Anda!\nBarang yg sudah dibeli tidak dapat ditukar dan dikembalikan.\n\n\n".encode('utf-8'))
            struk_data.extend(CUT_PAPER)

            printer.write(struk_data)
            printer.close()
            
        except Exception as e:
            messagebox.showwarning("Peringatan Printer", f"Transaksi sukses, tetapi gagal cetak struk Bluetooth:\n{e}")
            
            
if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiKasirModern(root)
    root.mainloop()
    