def enkripsi_sederhana(data, kunci="kunci"):
    """Fungsi Placeholder untuk enkripsi data"""
    return f"ENC({data})"

def deskripsi_data(transaksi):
    """Fungsi Placeholder untuk deskripsi data transaksi"""
    data_terenkripsi = transaksi['data_terenkripsi']
    return data_terenkripsi.replace("ENC(", "").replace(")", "")

def verifikasi_kata_sandi(pengguna, kata_sandi):
    """Memeriksa apakah hash_kata_sandi cocok dengan input kata sandi"""
    return pengguna['hash_kata_sandi'] == kata_sandi

def perbarui_saldo(akun, jumlah):
    """Menambahkan atau mengurangi saldo akun"""
    akun['saldo'] += jumlah

def dapatkan_id_berikutnya(bank):
    """Menghasilkan ID numerik unik untuk Pengguna/Akun/Transaksi."""
    bank['penghitung_id'] += 1
    return str(bank['penghitung_id'])

def generate_pin_acak():
    """Mengganti PIN acak dengan PIN default yang sudah ditentukan (PIN statis)"""
    return "987654"

def notifikasi_pengguna(bank, no_rekening_pengguna, pesan):
    """Menampilkan notifikasi sederhana"""
    pengguna = baca_pengguna(bank, no_rekening_pengguna)
    if pengguna:
        print(f"🔔 Notifikasi ke {pengguna['email']}: {pesan}")

def validasi_jumlah(jumlah):
    """Memastikan jumlah lebih dari nol"""
    if jumlah <= 0:
        return False
    return True

def buat_pengguna(bank, nama, email, pin, nik, ttl, no_telp, nama_ibu_kandung, alamat, saldo_awal=0.0, peran='nasabah'):
    """Membuat pengguna baru dengan detail tambahan dari Kode 1"""
    no_rekening = dapatkan_id_berikutnya(bank)
    pengguna = {
        'no_rekening': no_rekening,
        'nama': nama,
        'email': email,
        'alamat': alamat,
        'hash_kata_sandi': pin,
        'wajib_ganti_password': False,
        'peran': peran,
        'nik': nik,
        'ttl': ttl,
        'no_telp': no_telp,
        'nama_ibu_kandung': nama_ibu_kandung.lower() 
    }
    bank['pengguna'][no_rekening] = pengguna

    buat_akun(bank, no_rekening, saldo_awal)
    return no_rekening

def baca_pengguna(bank, no_rekening):
    """Mencari pengguna berdasarkan No Rekening"""
    return bank['pengguna'].get(no_rekening)

def perbarui_pengguna(bank, no_rekening, **kwargs):
    """Memperbarui detail pengguna (termasuk PIN/hash_kata_sandi)"""
    pengguna = bank['pengguna'].get(no_rekening)
    if pengguna:
        for kunci, nilai in kwargs.items():
            if kunci == 'pin':
                pengguna['hash_kata_sandi'] = nilai 
            else:
                pengguna[kunci] = nilai

def hapus_pengguna(bank, no_rekening):
    """Menghapus pengguna (dan akun terkait secara implisit)"""
    if no_rekening in bank['pengguna']:
        del bank['pengguna'][no_rekening]

def buat_akun(bank, no_rekening_pengguna, saldo_awal=0.0):
    """Membuat akun bank yang terhubung ke pengguna"""
    no_akun = no_rekening_pengguna
    akun = {
        'no_rekening': no_akun,
        'no_rekening_pengguna': no_rekening_pengguna,
        'saldo': saldo_awal,
        'status': 'aktif',
        'transaksi': []
    }
    bank['akun'][no_akun] = akun
    return no_akun

def baca_akun_by_user_id(bank, no_rekening_pengguna):
    """Mencari akun berdasarkan ID pengguna (karena 1 pengguna = 1 akun di simulasi ini)"""
    for acc in bank['akun'].values():
        if acc['no_rekening_pengguna'] == no_rekening_pengguna:
            return acc
    return None

def baca_akun(bank, no_rekening_akun):
    """Mencari akun berdasarkan No Akun bank"""
    return bank['akun'].get(no_rekening_akun)


def buat_transaksi(bank, no_rekening, jenis, jumlah, deskripsi):
    """Fungsi pembantu untuk mencatat transaksi"""
    id_transaksi = dapatkan_id_berikutnya(bank)
    transaksi = {
        'id_transaksi': id_transaksi,
        'no_rekening': no_rekening,
        'jenis': jenis,
        'jumlah': jumlah,
        'deskripsi': deskripsi,
        'tanggal': str(id_transaksi),
        'data_terenkripsi': enkripsi_sederhana(f"{jenis}:{jumlah}:{deskripsi}")
    }
    bank['transaksi'][id_transaksi] = transaksi
    akun = baca_akun(bank, no_rekening)
    if akun:
        akun['transaksi'].append(transaksi)
    return transaksi

def setor(bank, no_rekening_akun, jumlah):
    """Setor tunai ke akun."""
    akun = baca_akun(bank, no_rekening_akun)
    if akun and akun['status'] == 'aktif':
        perbarui_saldo(akun, jumlah)
        buat_transaksi(bank, no_rekening_akun, 'setor', jumlah, 'Setor tunai')
        notifikasi_pengguna(bank, akun['no_rekening_pengguna'], f"Setor Rp{jumlah:,} berhasil. Saldo baru: Rp{akun['saldo']:,}")
        return True
    return False

def tarik_tunai(bank, no_rekening_akun, jumlah):
    """Tarik tunai dari akun (adaptasi dari kode 1 & 2)"""
    akun = baca_akun(bank, no_rekening_akun)
    if not akun or akun['status'] != 'aktif':
        print("❌ Akun tidak aktif")
        return False

    if jumlah > akun['saldo']:
        print("❌ Saldo tidak mencukupi")
        return False
    
    perbarui_saldo(akun, -jumlah)
    buat_transaksi(bank, no_rekening_akun, 'tarik', jumlah, 'Tarik tunai')
    notifikasi_pengguna(bank, akun['no_rekening_pengguna'], f"Tarik Rp{jumlah:,} berhasil. Sisa saldo: Rp{akun['saldo']:,}")
    return True

def transfer(bank, no_rekening_dari, no_rekening_ke, jumlah, deskripsi='Transfer dana'):
    """Transfer antar rekening bank (sesuai kode 2)."""
    akun_dari = baca_akun(bank, no_rekening_dari)
    akun_ke = baca_akun(bank, no_rekening_ke)
    
    if not akun_dari or not akun_ke:
        print("❌ Rekening asal atau tujuan tidak ditemukan")
        return False
        
    if akun_dari['status'] != 'aktif':
        print("❌ Rekening asal tidak aktif")
        return False

    if akun_dari['saldo'] < jumlah:
        print("❌ Saldo tidak mencukupi")
        return False
    
    perbarui_saldo(akun_dari, -jumlah)
    perbarui_saldo(akun_ke, jumlah)
    
    buat_transaksi(bank, no_rekening_dari, 'transfer', jumlah, f'{deskripsi} ke Akun {no_rekening_ke}')
    buat_transaksi(bank, no_rekening_ke, 'setor', jumlah, f'Terima {deskripsi} dari Akun {no_rekening_dari}')

    notifikasi_pengguna(bank, akun_dari['no_rekening_pengguna'], f"{deskripsi} Rp{jumlah:,} ke {no_rekening_ke} berhasil. Saldo: Rp{akun_dari['saldo']:,}")
    return True


def buat_laporan_transaksi(bank, no_rekening_akun):
    """Membuat laporan riwayat transaksi untuk akun."""
    akun = baca_akun(bank, no_rekening_akun)
    if akun:
        laporan = "\n--- Riwayat Transaksi ---\n"
        if not akun['transaksi']:
            laporan += "Belum ada transaksi."
        else:
            for t in akun['transaksi']:
                desc = deskripsi_data(t)
                laporan += f"[{t['tanggal']}] {desc} | Jumlah: Rp{t['jumlah']:,}\n"
        return laporan
    return "Akun tidak ditemukan"


def autentikasi_pengguna(bank, nama_atau_email, kata_sandi):
    """Mencari dan mengautentikasi pengguna berdasarkan nama/email dan kata sandi (PIN)"""
    for pengguna in bank['pengguna'].values():
        if (pengguna['nama'] == nama_atau_email or pengguna['email'] == nama_atau_email) and \
           verifikasi_kata_sandi(pengguna, kata_sandi):
            return pengguna
    return None


def lupa_pin(bank, pengguna):
    """Proses Lupa PIN menggunakan Nama Ibu Kandung (Security Question)"""
    print("\n--- LUPA PIN ---")
    validasi = input("Masukkan Nama Ibu Kandung Anda: ").lower()

    if validasi == pengguna['nama_ibu_kandung']:
        print("✅ Validasi berhasil!")
        while True:
            pin_baru = input("Masukkan PIN Baru (6 digit angka): ")
            if pin_baru.isdigit() and len(pin_baru) == 6:
                perbarui_pengguna(bank, pengguna['no_rekening'], pin=pin_baru)
                print("✅ PIN berhasil diubah! Silakan login kembali")
                return True 
            print("PIN harus 6 digit angka.")
    else:
        print("❌ Nama Ibu Kandung salah. Gagal mengubah PIN")
        return False


PIN_ADMIN = "123456"

def tambah_nasabah(bank):
    """Fungsi Tambah Nasabah (Diperbarui dengan Validasi Email Unik)"""
    print("\n--- TAMBAH NASABAH BARU ---")
    while True:
        email = input("Masukkan Email: ")
        is_registered = any(p['email'] == email for p in bank['pengguna'].values())

        if is_registered:
            print("❌ Email sudah terdaftar. Silakan masukkan email yang berbeda")
        else:
            print(f"✅ Email '{email}' berhasil diverifikasi")
            break

    nama = input("Masukkan Nama: ")
    alamat = input("Masukkan Alamat: ")

    while True:
        nik = input("Masukkan NIK (16 digit): ")
        if nik.isdigit() and len(nik) == 16:
            break
        print("❌ NIK harus 16 digit angka.")

    ttl = input("Masukkan TTL (DD-MM-YYYY): ")
    no_telp = input("Masukkan No. Telpon: ")
    nama_ibu_kandung = input("Masukkan Nama Ibu Kandung (Untuk Lupa PIN): ")

    while True:
        pin = input("Masukkan PIN (6 digit angka): ")
        if pin.isdigit() and len(pin) == 6:
            break
        print("❌ PIN harus 6 digit angka.")
    
    saldo_awal = 0.0
    while saldo_awal < 50000:
        try:
            saldo_awal = float(input("Masukkan Saldo Awal (Min. 50000): "))
        except ValueError:
            print("❌ Saldo awal harus berupa angka. Diatur menjadi 0")
            saldo_awal = 0.0
            continue 
        if saldo_awal < 50000:
            print("❌ Saldo awal minimal harus 50000. Mohon masukkan kembali")

    no_rekening = buat_pengguna(bank, nama, email, pin, nik, ttl, no_telp, nama_ibu_kandung, alamat, saldo_awal, peran='nasabah')
    print(f"\n✅ Nasabah {nama} berhasil ditambahkan! No. Rekening Pengguna: {no_rekening}")


def tampilkan_data_nasabah(bank):
    """Menampilkan semua data nasabah (Admin, adaptasi kode 1)"""
    print("\n--- Data Nasabah Saat Ini ---")
    nasabah_list = [u for u in bank['pengguna'].values() if u['peran'] == 'nasabah']

    if not nasabah_list:
        print("Belum ada nasabah terdaftar")
        return

    print("Total Nasabah:", len(nasabah_list))
    for i, pengguna in enumerate(nasabah_list, 1):
        akun = baca_akun_by_user_id(bank, pengguna['no_rekening'])
        saldo = akun['saldo'] if akun else 0

        print(f"\n[{i}] No. Rek: {pengguna['no_rekening']} | Nama: {pengguna['nama']} | Saldo: Rp{saldo:,.0f}")
        print(f"    Email: {pengguna['email']} | NIK: {pengguna['nik']} | Telp: {pengguna['no_telp']}")

def menu_admin(bank, pengguna_admin):
    """Menu Admin (Diadaptasi dari kode 2)"""
    pin_input = input("Masukkan PIN Admin: ")
    if pin_input != PIN_ADMIN:
        print("❌ PIN Admin salah")
        return

    while True:
        print("\n=== MENU ADMIN ===")
        print("1. Tambah Nasabah")
        print("2. Ubah Data Nasabah (Nama/Email/Alamat)")
        print("3. Hapus Nasabah")
        print("4. Reset PIN Nasabah")
        print("5. Lihat Semua Data Nasabah")
        print("6. Lihat Daftar Akun dan Saldo")
        print("7. Lihat Laporan Transaksi Keseluruhan")
        print("8. Kembali ke Menu Utama")
        pilihan = input("Pilih Opsi: ")

        if pilihan == '1':
            tambah_nasabah(bank)
        elif pilihan == '2':
            no_rekening_pengguna = input("No Rekening Pengguna Nasabah yang Diubah: ")
            pengguna = baca_pengguna(bank, no_rekening_pengguna)
            if not pengguna or pengguna['peran'] != 'nasabah':
                print("❌ Nasabah tidak ditemukan")
                continue
            
            kwargs = {}
            kunci = input("Bidang yang diperbarui (nama/email/alamat/no_telp): ")
            nilai = input("Nilai baru: ")
            
            if kunci in ['nama', 'email', 'alamat', 'no_telp']:
                kwargs[kunci] = nilai
                perbarui_pengguna(bank, no_rekening_pengguna, **kwargs)
                print(f"✅ Nasabah {pengguna['nama']} diperbarui")
            else:
                print("❌ Bidang tidak valid")
                
        elif pilihan == '3':
            no_rekening_pengguna = input("No Rekening Pengguna Nasabah yang Dihapus: ")
            if baca_pengguna(bank, no_rekening_pengguna):
                 hapus_pengguna(bank, no_rekening_pengguna)
                 print("✅ Nasabah dihapus")
            else:
                 print("❌ Nasabah tidak ditemukan")
                 
        elif pilihan == '4':
            no_rekening_pengguna = input("No Rekening Pengguna Nasabah untuk Reset PIN: ")
            pengguna = baca_pengguna(bank, no_rekening_pengguna)
            if pengguna and pengguna['peran'] == 'nasabah':
                pin_baru = generate_pin_acak()
                perbarui_pengguna(bank, no_rekening_pengguna, pin=pin_baru, wajib_ganti_password=True)
                print(f"✅ PIN reset. PIN sementara: *{pin_baru}*. Nasabah harus mengganti PIN saat login")
            else:
                print("❌ Nasabah tidak ditemukan")
                
        elif pilihan == '5':
            tampilkan_data_nasabah(bank)
            
        elif pilihan == '6':
            print("\n--- Daftar Akun dan Saldo ---")
            for acc_id, acc in bank['akun'].items():
                pengguna_acc = baca_pengguna(bank, acc['no_rekening_pengguna'])
                nama = pengguna_acc['nama'] if pengguna_acc else "Tidak ditemukan"
                print(f"No Rekening Akun: {acc_id} | Nama: {nama} | Saldo: Rp{acc['saldo']:,.0f}")
                
        elif pilihan == '7':
            print("\n--- Laporan Transaksi Keseluruhan ---")
            if not bank['transaksi']:
                print("Belum ada transaksi tercatat")
            else:
                for tid, t in bank['transaksi'].items():
                    akun = baca_akun(bank, t['no_rekening'])
                    pengguna_t = baca_pengguna(bank, akun['no_rekening_pengguna']) if akun else None
                    nama = pengguna_t['nama'] if pengguna_t else "Tidak ditemukan"
                    print(f"No Rekening: {t['no_rekening']} | Nama: {nama} | Jenis: {t['jenis']} | Jumlah: Rp{t['jumlah']:,.0f} | Tanggal: {t['tanggal']}")
                    
        elif pilihan == '8':
            break
        else:
            print("Pilihan tidak valid")


def transfer_ewallet(bank, no_rekening_akun):
    """Transfer Dana ke E-Wallet (diadaptasi dari kode 1)"""
    print("\n--- TRANSFER DANA KE E-WALLET ---")
    akun = baca_akun(bank, no_rekening_akun)

    if akun['saldo'] <= 0:
        print("❌ Saldo tidak mencukupi untuk transfer")
        return
        
    print(f"Saldo Anda saat ini: Rp{akun['saldo']:,.0f}")

    print("\nPilih E-Wallet Tujuan:")
    EWALLETS = {'1': 'OVO', '2': 'GOPAY', '3': 'DANA', '4': 'SHOPEEPAY'}
    for k, v in EWALLETS.items():
         print(f"{k}. {v}")
         
    ew_pilihan = input("Pilihan (1-4): ")
    if ew_pilihan not in EWALLETS:
        print("❌ Pilihan E-Wallet tidak valid")
        return
        
    ew_nama = EWALLETS[ew_pilihan]

    no_hp_tujuan = input(f"Masukkan No. HP tujuan {ew_nama}: ")
    
    try:
        jumlah = float(input("Masukkan Jumlah Transfer: "))
    except ValueError:
        print("❌ Jumlah transfer harus berupa angka")
        return

    if not validasi_jumlah(jumlah):
        print("❌ Jumlah transfer harus lebih dari nol")
        return

    if jumlah > akun['saldo']:
        print("❌ Saldo tidak mencukupi untuk transfer sejumlah itu")
        return

    perbarui_saldo(akun, -jumlah)
    buat_transaksi(bank, no_rekening_akun, 'transfer_ewallet', jumlah, f'Transfer ke {ew_nama} No.HP {no_hp_tujuan}')

    print(f"\n🎉 Transfer Rp{jumlah:,.0f} ke {ew_nama} ({no_hp_tujuan}) berhasil!")
    print(f"Saldo Anda saat ini: Rp{akun['saldo']:,.0f}")

def menu_nasabah(bank, pengguna):
    """Menu Nasabah (Gabungan Kode 1 dan 2)."""
    
    akun = baca_akun_by_user_id(bank, pengguna['no_rekening'])
    if not akun:
        print("❌ Akun bank tidak ditemukan. Hubungi Admin")
        return

    print(f"\nSelamat datang, {pengguna['nama']}! No. Akun Anda: {akun['no_rekening']}")
    
    while True:
        print("\n=== MENU NASABAH ===")
        print("1. Cek Saldo")
        print("2. Lihat Riwayat Transaksi")
        print("3. Tarik Tunai")
        print("4. Setor Tunai")
        print("5. Transfer ke Rekening Bank Lain")
        print("6. Transfer ke E-Wallet")         
        print("7. Lupa/Ganti PIN/Password")
        print("8. Kembali ke Menu Utama")
        pilihan = input("Pilih Opsi: ")

        if pilihan == '1':
            akun_terbaru = baca_akun(bank, akun['no_rekening'])
            print(f"\n💰 Saldo Anda saat ini: Rp{akun_terbaru['saldo']:,.0f}")
            
        elif pilihan == '2':
            print(buat_laporan_transaksi(bank, akun['no_rekening']))
            
        elif pilihan == '3':
            try:
                jumlah = float(input("Masukkan Jumlah Tarik Tunai: "))
            except ValueError:
                print("❌ Input harus berupa angka")
                continue
            
            pin_input = input("Masukkan PIN Anda (6 digit) untuk konfirmasi: ")
            if pin_input != pengguna['hash_kata_sandi']:
                print("❌ PIN salah. Tarik tunai dibatalkan")
                continue
                
            if validasi_jumlah(jumlah):
                if tarik_tunai(bank, akun['no_rekening'], jumlah):
                    print("✅ Tarik tunai berhasil")
            else:
                print("❌ Jumlah tidak valid")
                
        elif pilihan == '4':
             try:
                jumlah = float(input("Masukkan Jumlah Setor Tunai: "))
             except ValueError:
                print("❌ Input harus berupa angka")
                continue
                
             if validasi_jumlah(jumlah):
                if setor(bank, akun['no_rekening'], jumlah):
                    print("✅ Setor tunai berhasil")
             else:
                 print("❌ Jumlah tidak valid")
                 
        elif pilihan == '5':
            no_rekening_tujuan = input("Nomor Rekening Tujuan: ")
            if no_rekening_tujuan == akun['no_rekening']:
                 print("❌ Tidak dapat transfer ke rekening sendiri")
                 continue

            try:
                jumlah = float(input("Jumlah Transfer: "))
            except ValueError:
                print("❌ Input harus berupa angka")
                continue

            pin_input = input("Masukkan PIN Anda (6 digit) untuk konfirmasi: ")
            if pin_input != pengguna['hash_kata_sandi']:
                print("❌ PIN salah. Transfer dibatalkan")
                continue

            if validasi_jumlah(jumlah):
                if transfer(bank, akun['no_rekening'], no_rekening_tujuan, jumlah):
                    print("✅ Transfer dana berhasil")
            else:
                print("❌ Transfer tidak dapat dilakukan (Jumlah tidak valid)")

        elif pilihan == '6':
             pin_input = input("Masukkan PIN Anda (6 digit) untuk konfirmasi: ")
             if pin_input != pengguna['hash_kata_sandi']:
                print("❌ PIN salah. Transfer dibatalkan")
                continue
             transfer_ewallet(bank, akun['no_rekening'])

        elif pilihan == '7':
             pilihan_reset = input("Lupa PIN atau Ganti PIN? (lupa/ganti): ").lower()
             if pilihan_reset == 'lupa':
                 lupa_pin(bank, pengguna) 
                 pin_baru = input("Masukkan PIN baru Anda untuk melanjutkan: ")
                 if pin_baru == pengguna['hash_kata_sandi']:
                     print("✅ Otentikasi berhasil, melanjutkan ke Menu Nasabah")
                 else:
                     print("❌ PIN salah, kembali ke Menu Utama")
                     return
             elif pilihan_reset == 'ganti':
                 kata_sandi_lama = input("PIN Lama: ")
                 if verifikasi_kata_sandi(pengguna, kata_sandi_lama):
                      kata_sandi_baru = input("PIN Baru (6 digit): ")
                      konfirmasi = input("Konfirmasi PIN Baru: ")
                      if kata_sandi_baru.isdigit() and len(kata_sandi_baru) == 6 and kata_sandi_baru == konfirmasi:
                          perbarui_pengguna(bank, pengguna['no_rekening'], pin=kata_sandi_baru, wajib_ganti_password=False)
                          print("✅ PIN berhasil diubah.")
                      else:
                          print("❌ PIN harus 6 digit angka dan konfirmasi tidak cocok")
                 else:
                      print("❌ PIN lama salah")
             else:
                 print("Pilihan tidak valid")

        elif pilihan == '8':
            break
        else:
            print("Pilihan tidak valid")


def utama():
    """Fungsi utama program"""
    bank = {
        'penghitung_id': 0, 
        'pengguna': {},
        'akun': {},
        'transaksi': {}
    }

    admin_id = "ADMIN001"
    bank['pengguna'][admin_id] = {
        'no_rekening': admin_id,
        'nama': 'Admin',
        'email': 'admin@bank.com',
        'hash_kata_sandi': PIN_ADMIN, 
        'peran': 'admin',
    }
    dummy_admin = bank['pengguna'][admin_id]


    while True:
        print("\n==========================")
        print("=== APLIKASI PERBANKAN ===")
        print("==========================")
        print("1. Admin")
        print("2. Nasabah")
        
        pilihan = input("Pilih Menu (1-2): ")

        if pilihan == '1':
            menu_admin(bank, dummy_admin)
            
        elif pilihan == '2':
            nasabah_list = [u for u in bank['pengguna'].values() if u['peran'] == 'nasabah']
            if not nasabah_list:
                print("Belum ada nasabah terdaftar. Silakan buat akun melalui menu Admin terlebih dahulu.")
                continue

            print("\n--- LOGIN NASABAH ---")
            nama_atau_email = input("Nama atau Email Nasabah: ")
            kata_sandi = input("PIN/Password Nasabah: ")

            pengguna = autentikasi_pengguna(bank, nama_atau_email, kata_sandi)

            if pengguna and pengguna['peran'] == 'nasabah':
                if pengguna.get('wajib_ganti_password'):
                    print("\n⚠ PIN/Password sementara terdeteksi. Anda harus mengganti PIN")
                    pin_baru = input("Masukkan PIN baru (6 digit): ")
                    konfirmasi = input("Konfirmasi PIN baru: ")
                    
                    if pin_baru.isdigit() and len(pin_baru) == 6 and pin_baru == konfirmasi:
                        perbarui_pengguna(bank, pengguna['no_rekening'], pin=pin_baru, wajib_ganti_password=False)
                        print("✅ PIN berhasil diubah. Silakan lanjutkan.")
                    else:
                        print("❌ PIN harus 6 digit angka dan konfirmasi tidak cocok. Kembali ke Menu Utama")
                        continue

                menu_nasabah(bank, pengguna)
                
            else:
                 print("❌ Kredensial nasabah tidak valid")

        else:
            print("Pilihan tidak valid. Silakan pilih 1, atau 2")

utama()