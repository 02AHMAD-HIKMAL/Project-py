import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import serial

def inisialisasi_db():
    conn = sqlite3.connect("toko_kelontong.db")
    cursor = conn.cursor()
    # Tabel Produk
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produk (
            kode TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL
        )
    """
    )

    
    cursor.execute("SELECT COUNT(*) FROM produk")
    if cursor.fetchone()[0] == 0:
        data_awal = [
            ("A01", "Beras 5kg", 65000, 20),
            ("A02", "Minyak Goreng 1L", 18000, 30),
            ("A03", "Gula Pasir 1kg", 16000, 25),
            ("A04", "Telur 1kg", 28000, 15),
            ("A05", "Mie Instan (Dus)", 110000, 10),
        ]
        cursor.executemany(
            "INSERT INTO produk VALUES (?, ?, ?, ?)", data_awal
        )
        conn.commit()
    conn.close()


class AplikasiKasir:

    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Kasir Toko Kelontong")
        self.root.geometry("900x600")

        inisialisasi_db()
        self.keranjang = []

        
        
        lbl_judul = tk.Label(
            root,
            text="TOKO MALLCELL - KASIR",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10,
        )
        lbl_judul.pack(fill=tk.X)

       
        frame_utama = tk.Frame(root, padx=10, pady=10)
        frame_utama.pack(fill=tk.BOTH, expand=True)

        
        frame_kiri = tk.Frame(frame_utama)
        frame_kiri.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            frame_kiri, text="Daftar Barang Tersedia", font=("Arial", 12, "bold")
        ).pack(anchor="w")

        # Tabel Daftar Produk
        self.tree_produk = ttk.Treeview(
            frame_kiri, columns=("Kode", "Nama", "Harga", "Stok"), show="headings"
        )
        self.tree_produk.heading("Kode", text="Kode")
        self.tree_produk.heading("Nama", text="Nama Barang")
        self.tree_produk.heading("Harga", text="Harga (Rp)")
        self.tree_produk.heading("Stok", text="Stok")
        self.tree_produk.column("Kode", width=60)
        self.tree_produk.column("Nama", width=150)
        self.tree_produk.column("Harga", width=90)
        self.tree_produk.column("Stok", width=50)
        self.tree_produk.pack(fill=tk.BOTH, expand=True, pady=5)

        
        frame_input = tk.Frame(frame_kiri, pady=5)
        frame_input.pack(fill=tk.X)

        tk.Label(frame_input, text="Jumlah Beli:").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.entry_jumlah = tk.Entry(frame_input, width=10, font=("Arial", 11))
        self.entry_jumlah.pack(side=tk.LEFT, padx=(0, 10))

        btn_tambah = tk.Button(
            frame_input,
            text="Tambah ke Keranjang",
            bg="#27ae60",
            fg="white",
            command=self.tambah_ke_keranjang,
        )
        btn_tambah.pack(side=tk.LEFT)

        
        frame_kanan = tk.Frame(frame_utama, width=350)
        frame_kanan.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        tk.Label(
            frame_kanan, text="Keranjang Belanja", font=("Arial", 12, "bold")
        ).pack(anchor="w")

        
        self.tree_keranjang = ttk.Treeview(
            frame_kanan,
            columns=("Nama", "Qty", "Subtotal"),
            show="headings",
            height=10,
        )
        self.tree_keranjang.heading("Nama", text="Item")
        self.tree_keranjang.heading("Qty", text="Qty")
        self.tree_keranjang.heading("Subtotal", text="Subtotal")
        self.tree_keranjang.column("Nama", width=140)
        self.tree_keranjang.column("Qty", width=40)
        self.tree_keranjang.column("Subtotal", width=90)
        self.tree_keranjang.pack(fill=tk.BOTH, pady=5)

        btn_hapus_item = tk.Button(
            frame_kanan,
            text="Hapus Item Terpilih",
            bg="#c0392b",
            fg="white",
            command=self.hapus_item_keranjang,
        )
        btn_hapus_item.pack(fill=tk.X, pady=(0, 10))

        
        frame_bayar = tk.LabelFrame(
            frame_kanan, text="Pembayaran", font=("Arial", 10, "bold"), padx=10, pady=10
        )
        frame_bayar.pack(fill=tk.X, pady=5)

        tk.Label(
            frame_bayar, text="TOTAL:", font=("Arial", 11, "bold")
        ).grid(row=0, column=0, sticky="w")
        self.lbl_total_val = tk.Label(
            frame_bayar, text="Rp 0", font=("Arial", 12, "bold"), fg="#c0392b"
        )
        self.lbl_total_val.grid(row=0, column=1, sticky="e")

        tk.Label(frame_bayar, text="Uang Tunai:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.entry_bayar = tk.Entry(frame_bayar, font=("Arial", 11), width=12)
        self.entry_bayar.grid(row=1, column=1, sticky="e", pady=5)

        btn_proses = tk.Button(
            frame_bayar,
            text="Proses & Cetak Struk (BT)",
            bg="#2980b9",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.proses_transaksi,
        )
        btn_proses.grid(row=2, column=0, columnspan=2, sticky="we", pady=10)

        
        self.muat_data_produk()

    def muat_data_produk(self):
        
        for item in self.tree_produk.get_children():
            self.tree_produk.delete(item)

        conn = sqlite3.connect("toko_kelontong.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produk")
        for baris in cursor.fetchall():
            self.tree_produk.insert(
                "", tk.END, values=(baris[0], baris[1], f"Rp {baris[2]:,}", baris[3])
            )
        conn.close()

    def tambah_ke_keranjang(self):
        selected_item = self.tree_produk.selection()
        if not selected_item:
            messagebox.showwarning(
                "Peringatan", "Pilih barang terlebih dahulu dari daftar!"
            )
            return

        qty_str = self.entry_jumlah.get()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showerror(
                "Error", "Masukkan jumlah beli yang valid (angka > 0)!"
            )
            return

        qty = int(qty_str)
        item_data = self.tree_produk.item(selected_item)
        kode = item_data["values"][0]
        nama = item_data["values"][1]
        # Bersihkan format harga dari string "Rp " dan koma
        harga = int(
            item_data["values"][2].replace("Rp ", "").replace(",", "")
        )
        stok_tersedia = int(item_data["values"][3])

        if qty > stok_tersedia:
            messagebox.showerror(
                "Error", f"Stok tidak mencukupi! Sisa stok: {stok_tersedia}"
            )
            return

        
        for item in self.keranjang:
            if item["kode"] == kode:
                if item["jumlah"] + qty > stok_tersedia:
                    messagebox.showerror(
                        "Error", "Jumlah melebihi total stok yang ada!"
                    )
                    return
                item["jumlah"] += qty
                item["subtotal"] = item["jumlah"] * harga
                self.update_tampilan_keranjang()
                self.entry_jumlah.delete(0, tk.END)
                return

        
        self.keranjang.append(
            {
                "kode": kode,
                "nama": nama,
                "harga": harga,
                "jumlah": qty,
                "subtotal": harga * qty,
            }
        )
        self.update_tampilan_keranjang()
        self.entry_jumlah.delete(0, tk.END)

    def hapus_item_keranjang(self):
        selected_item = self.tree_keranjang.selection()
        if not selected_item:
            messagebox.showwarning(
                "Peringatan", "Pilih item di keranjang yang ingin dihapus!"
            )
            return

        index = self.tree_keranjang.index(selected_item)
        del self.keranjang[index]
        self.update_tampilan_keranjang()

    def update_tampilan_keranjang(self):
        for item in self.tree_keranjang.get_children():
            self.tree_keranjang.delete(item)

        total_belanja = 0
        for item in self.keranjang:
            self.tree_keranjang.insert(
                "",
                tk.END,
                values=(
                    item["nama"],
                    item["jumlah"],
                    f"Rp {item['subtotal']:,}",
                ),
            )
            total_belanja += item["subtotal"]

        self.lbl_total_val.config(text=f"Rp {total_belanja:,}")

    def hitung_total_belanja(self):
        return sum(item["subtotal"] for item in self.keranjang)

    def proses_transaksi(self):
        if not self.keranjang:
            messagebox.showwarning("Peringatan", "Keranjang masih kosong!")
            return

        bayar_str = self.entry_bayar.get()
        if not bayar_str.isdigit():
            messagebox.showerror(
                "Error", "Masukkan nominal uang tunai yang valid!"
            )
            return

        bayar = int(bayar_str)
        total_belanja = self.hitung_total_belanja()

        if bayar < total_belanja:
            messagebox.showerror(
                "Error",
                f"Uang tunai kurang! Kurang Rp {total_belanja - bayar:,}",
            )
            return

        kembalian = bayar - total_belanja


        
        conn = sqlite3.connect("toko_kelontong.db")
        cursor = conn.cursor()
        for item in self.keranjang:
            cursor.execute(
                "UPDATE produk SET stok = stok - ? WHERE kode = ?",
                (item["jumlah"], item["kode"]),
            )
        conn.commit()
        conn.close()

        self.cetak_ke_bluetooth_thermal(total_belanja, bayar, kembalian)
        
        messagebox.showinfo(
            "Sukses",
            f"Transaksi Berhasil!\nUang Kembalian: Rp {kembalian:,}",
        )
        self.keranjang.clear()
        self.update_tampilan_keranjang()
        self.entry_bayar.delete(0, tk.END)
        self.muat_data_produk()

    def cetak_ke_bluetooth_thermal(self, total_belanja, bayar, kembalian):
        PORT_BLUETOOTH = "COM7" 
        BAUD_RATE = 9600

        try:
            printer = serial.Serial(PORT_BLUETOOTH, BAUD_RATE, timeout=1)

            INIT = b"\x1b\x40"
            ALIGN_CENTER = b"\x1b\x61\x01"
            ALIGN_LEFT = b"\x1b\x61\x00"
            BOLD_ON = b"\x1b\x45\x01"
            BOLD_OFF = b"\x1b\x45\x00"
            CUT_PAPER = b"\x1d\x56\x42\x00"

            struk_data = bytearray()
            struk_data.extend(INIT)

            
            struk_data.extend(ALIGN_CENTER)
            struk_data.extend(BOLD_ON)
            struk_data.extend("TOKO MALLCELL\n".encode("utf-8"))
            struk_data.extend(BOLD_OFF)
            struk_data.extend("Jl. Raya Kediri\n".encode("utf-8"))
            struk_data.extend(("-" * 32 + "\n").encode("utf-8"))

            # Item
            struk_data.extend(ALIGN_LEFT)
            for item in self.keranjang:
                struk_data.extend(f"{item['nama'][:32]}\n".encode("utf-8"))
                struk_data.extend(
                    f"  {item['jumlah']} x {item['harga']:,} = {item['subtotal']:,}\n".encode(
                        "utf-8"
                    )
                )

            struk_data.extend(("-" * 32 + "\n").encode("utf-8"))
            struk_data.extend(BOLD_ON)
            struk_data.extend(
                f"TOTAL   : Rp {total_belanja:,}\n".encode("utf-8")
            )
            struk_data.extend(f"BAYAR   : Rp {bayar:,}\n".encode("utf-8"))
            struk_data.extend(f"KEMBALI : Rp {kembalian:,}\n".encode("utf-8"))
            struk_data.extend(BOLD_OFF)

            struk_data.extend(("-" * 32 + "\n").encode("utf-8"))
            struk_data.extend(ALIGN_CENTER)
            struk_data.extend(
                "Terima Kasih Atas Kunjungan Anda!\nBarang yang sudah dibeli tidak  dapat ditukar/dikembalikan.\n\n\n".encode(
                    "utf-8"
                )
            )
            struk_data.extend(CUT_PAPER)

            printer.write(struk_data)
            printer.close()

        except Exception as e:
            messagebox.showwarning(
                "Peringatan Printer",
                f"Transaksi berhasil, tetapi gagal cetak struk via Bluetooth:\n{e}",
            )


# ==================== MENJALANKAN APLIKASI ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiKasir(root)
    root.mainloop()