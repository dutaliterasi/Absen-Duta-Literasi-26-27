import streamlit as st
import pandas as pd
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA CUTE
# ==========================================
st.set_page_config(
    page_title="Absensi Duta Literasi MTsN 1 Jember",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk tampilan Mobile-Friendly & Pastel Cute
st.markdown("""
    <style>
    /* Latar Belakang Pastel Lembut */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E0F7FA 50%, #FFF9C4 100%);
        font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
    }
    /* Kartu Kontainer Utama */
    .main-card {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 25px;
        border: 3px solid #FF80AB;
        box-shadow: 0 8px 16px rgba(255, 128, 171, 0.2);
        margin-bottom: 20px;
    }
    /* Judul Utama */
    .title-text {
        color: #D81B60;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .subtitle-text {
        color: #00838F;
        text-align: center;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    /* Tombol Simpan */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FF4081, #FF80AB);
        color: white;
        font-weight: bold;
        font-size: 18px;
        border-radius: 20px;
        border: none;
        padding: 12px;
        box-shadow: 0 4px 10px rgba(255, 64, 129, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #F50057, #FF4081);
    }
    /* Lencana Karakter */
    .char-badge {
        display: inline-block;
        background-color: #FCE4EC;
        color: #C2185B;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 13px;
        font-weight: bold;
        margin: 3px;
        border: 1px solid #F48FB1;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ANGGOTA DUTA LITERASI (SILAKAN EDIT)
# ==========================================
DAFTAR_ANGGOTA = [
    "-- Pilih Nama Anggota --",
    "Dramalia Melody Yudha",
    "Debbynda Putri Azzahra",
    "Primaloka Ratu Jingga",
    "Zayyana Alkhaira Najia Syakira",
    "Ranaa Anindya Gantari",
    "Naomi Tazkia Pramana Putri",
    "Matsna Fawnia Khairunnisa",
    "Zaskia Ulya Narendra",
    "Calysta Syafiqa Salsa Billa",
    "Diera Havva Zakiah",
    "Adia Rafa Fathina",
    "Nadin Farrahatun Nisa Purmono",
    "Haikal Tijani Daniswara",
    "Dafhina Adinda Putri",
    "Aaqilah Shafa Ays Fathoni",
    "Akifah Hafiza Khairani",
    "Shabira Yumna Maswariya",
    "As Sayyidah Hannah Al-Humaira",
    "Razka Nizam Syahzani",
    "Nafilah Firyal Adibah",
    "Rafania Dian Nugraha",
    "Zakkiya Izza Afkarina",
    "Nada Aqila Azziada",
    "Bintany Izza Bulghaturizqi",
    "Syua Nazila Salwa",
    "Afiqah Nur Wakhidah",
    "Annisa Kirana Maheswari",
    "Ainil Balqis Izza Valentino",
    "Indah Kurnia Rahayu",
    "Wilda Kamelia Rahma",
    "Yasmin Aulia Arifa",
    "Mikayla Callista Arifin",
    "Allya Mahira Rasyidah",
    "Syakira Azalia Sugiarto",
    "Syifa Aurellia Callista Dwi Artanti",
    "Azzahra Raissa Putri Fiedi Elysia",
    "Anisah Dyah Pramesti",
    "Oktaviana Eka Juna",

]

# Pilihan Tema Karakter Cute
TEMA_KARAKTER = {
    "🐻 Masha & The Bear (Ceria & Usil)": {"emoji": "👧🏼🐻", "quotes": "Semangat baca buku bareng Masha dan Beruang!"},
    "🦈 Baby Shark (Doo Doo Doo!)": {"emoji": "🦈🌊", "quotes": "Literasi seru, doo doo doo doo doo doo!"},
    "⚡ Pokémon (Gotta Read 'Em All!)": {"emoji": "⚡🔴", "quotes": "Pika-Pika! Kumpulkan ilmu sebanyak menangkap Pokémon!"},
    "👦👦 Upin & Ipin (Betul! Betul! Betul!)": {"emoji": "🐔🍧", "quotes": "Membaca jambatan ilmu! Betul, betul, betul!"},
    "🧢 BoBoiBoy (Kuasa Elemental!)": {"emoji": "⚡🌪️🔥", "quotes": "BoBoiBoy Kuasa Literasi! Terbaik!"},
    "🐭 Mickey Mouse (Klasik Disney)": {"emoji": "🎀🐭", "quotes": "Oh Boy! Waktunya menjaga perpustakaan dengan ceria!"},
    "👑 Sofia the First (Putri Kerajaan)": {"emoji": "👑💜", "quotes": "Setiap halaman buku membuka dunia kerajaan baru!"}
}

# ==========================================
# 3. FUNGSI PENYIMPANAN OTOMATIS & GOOGLE SHEETS
# ==========================================
FILE_LOKAL = "rekap_absensi_duta_literasi.csv"

def simpan_data_otomatis(nama, tanggal, status, karakter, catatan):
    waktu_input = datetime.now().strftime("%H:%M:%S")
    data_baru = pd.DataFrame([{
        "Tanggal": tanggal.strftime("%Y-%m-%d"),
        "Waktu Input": waktu_input,
        "Nama Siswa": nama,
        "Status": status,
        "Tema Karakter": karakter,
        "Catatan": catatan
    }])

    # A. Penyimpanan Otomatis ke File Lokal (Backup Aman)
    if os.path.exists(FILE_LOKAL):
        data_lama = pd.read_csv(FILE_LOKAL)
        data_gabungan = pd.concat([data_lama, data_baru], ignore_index=True)
    else:
        data_gabungan = data_baru
    data_gabungan.to_csv(FILE_LOKAL, index=False)

    # B. Sinkronisasi ke Google Sheets (Jika credentials.json tersedia)
    status_gsheet = "Tersimpan di HP/Server Lokal (Mode Offline/Backup)"
    if os.path.exists("credentials.json"):
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
            client = gspread.authorize(creds)
            # Ganti nama file sesuai nama Google Sheets milikmu
            sheet = client.open("Absensi Duta Literasi MTsN 1 Jember").sheet1
            sheet.append_row([
                tanggal.strftime("%Y-%m-%d"),
                waktu_input,
                nama,
                status,
                karakter,
                catatan
            ])
            status_gsheet = "Berhasil tersinkronisasi langsung ke Google Sheets! ☁️"
        except Exception as e:
            status_gsheet = f"Tersimpan di Lokal (Google Sheets belum terhubung: {e})"
            
    return status_gsheet

# ==========================================
# 4. TAMPILAN ANTARMUKA (UI) MOBILE FRIENDLY
# ==========================================
st.markdown("""
    <div class="main-card">
        <div class="title-text">📚 Duta Literasi Perpustakaan</div>
        <div class="subtitle-text">MTs Negeri 1 Jember ✨</div>
        <div style="text-align: center;">
            <span class="char-badge">🐻 Masha</span>
            <span class="char-badge">🦈 Baby Shark</span>
            <span class="char-badge">⚡ Pokémon</span>
            <span class="char-badge">👦 Upin Ipin</span>
            <span class="char-badge">🧢 BoBoiBoy</span>
            <span class="char-badge">🐭 Mickey</span>
            <span class="char-badge">👑 Sofia</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Form Kehadiran
with st.container():
    # Pilih Karakter Mood Hari Ini
    karakter_pilihan = st.selectbox(
        "🎀 Pilih Karakter Teman Piket Hari Ini:",
        list(TEMA_KARAKTER.keys())
    )
    info_karakter = TEMA_KARAKTER[karakter_pilihan]
    st.info(f"{info_karakter['emoji']} **{info_karakter['quotes']}**")

    # Input Nama Siswa
    nama_siswa = st.selectbox("👤 Nama Anggota Duta Literasi:", DAFTAR_ANGGOTA)

    # Input Tanggal Kehadiran
    tanggal_hadir = st.date_input("📅 Tanggal Kehadiran:", datetime.now())

    # Input Status Kehadiran
    status_kehadiran = st.radio(
        "📌 Status Kehadiran:",
        ["✅ Hadir", "✉️ Izin", "🤒 Sakit", "❌ Alpha"],
        horizontal=True
    )

    # Catatan Tambahan (Opsional)
    catatan = st.text_input("📝 Catatan / Keterangan (Opsional):", placeholder="Contoh: Piket jaga perpustakaan jam istirahat")

    st.write("")
    # Tombol Submit
    if st.button("💖 Simpan Kehadiran Sekarang"):
        if nama_siswa == "-- Pilih Nama Anggota --":
            st.warning("⚠️ Pilih nama kamu dulu ya sebelum menyimpan!")
        else:
            hasil = simpan_data_otomatis(nama_siswa, tanggal_hadir, status_kehadiran, karakter_pilihan, catatan)
            st.balloons()
            st.success(f"Yeay! Absensi **{nama_siswa}** ({status_kehadiran}) sudah dicatat otomatis!")
            st.caption(f"Status Penyimpanan: {hasil}")

# ==========================================
# 5. REKAP DATA REAL-TIME & UNDUH EXCEL/CSV
# ==========================================
st.markdown("---")
st.subheader("📊 Rekap Kehadiran Hari Ini")

if os.path.exists(FILE_LOKAL):
    df_rekap = pd.read_csv(FILE_LOKAL)
    st.dataframe(df_rekap.tail(10), use_container_width=True)
    
    # Tombol Unduh Rekap untuk Laporan
    csv_data = df_rekap.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Rekap Absensi (.CSV / Excel)",
        data=csv_data,
        file_name=f"Rekap_Duta_Literasi_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.caption("Belum ada data kehadiran yang masuk hari ini. Yuk isi absen pertama!")
