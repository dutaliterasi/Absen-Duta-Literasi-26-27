From datetime import datetime
import os
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA CUTE
# ==========================================
st.set_page_config(
    page_title="Absensi Duta Literasi MTsN 1 Jember",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS untuk tampilan Mobile-Friendly & Pastel Cute
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. DATA ANGGOTA DUTA LITERASI
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
    "🐻 Masha & The Bear (Ceria & Usil)": {
        "emoji": "👧🏼🐻",
        "quotes": "Semangat baca buku bareng Masha dan Beruang!",
    },
    "🦈 Baby Shark (Doo Doo Doo!)": {
        "emoji": "🦈🌊",
        "quotes": "Literasi seru, doo doo doo doo doo doo!",
    },
    "⚡ Pokémon (Gotta Read 'Em All!)": {
        "emoji": "⚡🔴",
        "quotes": "Pika-Pika! Kumpulkan ilmu sebanyak menangkap Pokémon!",
    },
    "👦👦 Upin & Ipin (Betul! Betul! Betul!)": {
        "emoji": "🐔🍧",
        "quotes": "Membaca jambatan ilmu! Betul, betul, betul!",
    },
    "🧢 BoBoiBoy (Kuasa Elemental!)": {
        "emoji": "⚡🌪️🔥",
        "quotes": "BoBoiBoy Kuasa Literasi! Terbaik!",
    },
    "🐭 Mickey Mouse (Klasik Disney)": {
        "emoji": "🎀🐭",
        "quotes": "Oh Boy! Waktunya menjaga perpustakaan dengan ceria!",
    },
    "👑 Sofia the First (Putri Kerajaan)": {
        "emoji": "👑💜",
        "quotes": "Setiap halaman buku membuka dunia kerajaan baru!",
    },
}

# ==========================================
# 3. KONFIGURASI GOOGLE FORM & PENYIMPANAN
# ==========================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeCb02zXXPpwmd3h-N359jULDITYXflWrZUfFajGSOZFJpQJA/formResponse"
SHEET_ID = "1NIXzAi9Vcb7xIMH5XVQlyJklF8ZorvxYM8Cn_WZcfyw"
CSV_READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
FILE_LOKAL = "rekap_absensi_duta_literasi.csv"


def simpan_data_otomatis(nama, tanggal, status, karakter, catatan):
  waktu_input = datetime.now().strftime("%H:%M:%S")
  tgl_str = tanggal.strftime("%Y-%m-%d")

  # 1. Simpan ke Backup Lokal
  data_baru = pd.DataFrame([{
      "Tanggal": tgl_str,
      "Waktu Input": waktu_input,
      "Nama Siswa": nama,
      "Status": status,
      "Tema Karakter": karakter,
      "Catatan": catatan,
  }])

  if os.path.exists(FILE_LOKAL):
    data_lama = pd.read_csv(FILE_LOKAL)
    data_gabungan = pd.concat([data_lama, data_baru], ignore_index=True)
  else:
    data_gabungan = data_baru
  data_gabungan.to_csv(FILE_LOKAL, index=False)

  # 2. Kirim Permanen ke Google Sheets via Google Form
  catatan_lengkap = f"[{tanggal.strftime('%d-%m-%Y')}] {catatan}".strip()
  form_data = {
      "entry.1605593113": nama,
      "entry.1825141577": status,
      "entry.1914097499": karakter,
      "entry.1864582280": catatan_lengkap,
  }

  try:
    res = requests.post(FORM_URL, data=form_data, timeout=10)
    if res.status_code == 200:
      return "Berhasil tersimpan ke Google Sheets & Lokal! ☁️✨"
    else:
      return "Tersimpan di backup lokal (Gagal kirim ke Form)."
  except Exception as e:
    return f"Tersimpan di backup lokal (Error koneksi: {e})"


def muat_data_rekap():
  # Ambil data langsung dari Google Sheets (jika tersambung)
  try:
    df_gs = pd.read_csv(CSV_READ_URL)
    if not df_gs.empty and "Timestamp" in df_gs.columns:
      df_gs["Timestamp_dt"] = pd.to_datetime(
          df_gs["Timestamp"], errors="coerce"
      )
      df_gs["Tanggal"] = df_gs["Timestamp_dt"].dt.strftime("%Y-%m-%d")
      df_gs["Waktu Input"] = df_gs["Timestamp_dt"].dt.strftime("%H:%M:%S")
      df_gs = df_gs.rename(
          columns={
              "Nama": "Nama Siswa",
              "Karakter": "Tema Karakter",
          }
      )
      kolom_tampil = [
          c
          for c in [
              "Tanggal",
              "Waktu Input",
              "Nama Siswa",
              "Status",
              "Tema Karakter",
              "Catatan",
          ]
          if c in df_gs.columns
      ]
      return df_gs[kolom_tampil]
  except Exception:
    pass

  # Fallback ke file CSV lokal jika Sheets belum merespons
  if os.path.exists(FILE_LOKAL):
    return pd.read_csv(FILE_LOKAL)
  return pd.DataFrame()


# ==========================================
# 4. TAMPILAN ANTARMUKA (UI) MOBILE FRIENDLY
# ==========================================
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Form Kehadiran
with st.container():
  karakter_pilihan = st.selectbox(
      "🎀 Pilih Karakter Teman Piket Hari Ini:", list(TEMA_KARAKTER.keys())
  )
  info_karakter = TEMA_KARAKTER[karakter_pilihan]
  st.info(f"{info_karakter['emoji']} **{info_karakter['quotes']}**")

  nama_siswa = st.selectbox("👤 Nama Anggota Duta Literasi:", DAFTAR_ANGGOTA)

  tanggal_hadir = st.date_input(
      "📅 Tanggal Kehadiran:", datetime.now(), format="DD/MM/YYYY"
  )

  status_kehadiran = st.radio(
      "📌 Status Kehadiran:",
      ["✅ Hadir", "✉️ Izin", "🤒 Sakit", "❌ Alpha"],
      horizontal=True,
  )

  catatan = st.text_input(
      "📝 Catatan / Keterangan (Opsional):",
      placeholder="Contoh: Piket jaga perpustakaan jam istirahat",
  )

  st.write("")
  if st.button("💖 Simpan Kehadiran Sekarang"):
    if nama_siswa == "-- Pilih Nama Anggota --":
      st.warning("⚠️ Pilih nama kamu dulu ya sebelum menyimpan!")
    else:
      hasil = simpan_data_otomatis(
          nama_siswa,
          tanggal_hadir,
          status_kehadiran,
          karakter_pilihan,
          catatan,
      )
      st.balloons()
      st.success(
          f"Yeay! Absensi **{nama_siswa}** ({status_kehadiran}) sudah dicatat"
          " otomatis!"
      )
      st.caption(f"Status Penyimpanan: {hasil}")

# ==========================================
# 5. REKAP DATA DENGAN FILTER PILIH TANGGAL
# ==========================================
st.markdown("---")
st.subheader("📊 Rekap Kehadiran Duta Literasi")

df_rekap = muat_data_rekap()

if not df_rekap.empty:
  df_rekap["Tanggal"] = df_rekap["Tanggal"].astype(str)

  # Fitur Filter Tanggal (Sesuai Permintaan)
  tanggal_filter = st.date_input(
      "🔍 Pilih Tanggal Rekap:",
      value=datetime.now(),
      format="DD/MM/YYYY",
      key="filter_tanggal_rekap",
  )

  tanggal_str = tanggal_filter.strftime("%Y-%m-%d")
  tanggal_tampil = tanggal_filter.strftime("%d-%m-%Y")

  # Filter data khusus tanggal yang dipilih user
  df_filtered = df_rekap[df_rekap["Tanggal"] == tanggal_str]

  st.markdown(f"**Menampilkan data khusus tanggal: `{tanggal_tampil}`**")

  if not df_filtered.empty:
    # Metrik ringkas jumlah status pada tanggal tersebut
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ Hadir", len(df_filtered[df_filtered["Status"] == "✅ Hadir"]))
    col2.metric("✉️ Izin", len(df_filtered[df_filtered["Status"] == "✉️ Izin"]))
    col3.metric("🤒 Sakit", len(df_filtered[df_filtered["Status"] == "🤒 Sakit"]))
    col4.metric("❌ Alpha", len(df_filtered[df_filtered["Status"] == "❌ Alpha"]))

    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

    # Tombol Unduh Khusus Tanggal Terpilih
    csv_harian = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Unduh Rekap Tanggal {tanggal_tampil} (.CSV)",
        data=csv_harian,
        file_name=f"Rekap_Duta_Literasi_{tanggal_tampil}.csv",
        mime="text/csv",
        key="download_harian",
    )
  else:
    st.info(f"📭 Belum ada data absensi untuk tanggal **{tanggal_tampil}**.")

  # Opsi unduh keseluruhan data
  with st.expander("📂 Unduh Semua Data Rekap (Keseluruhan)"):
    csv_semua = df_rekap.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Semua Rekap Absensi (.CSV)",
        data=csv_semua,
        file_name=(
            f"Rekap_Semua_Duta_Literasi_{datetime.now().strftime('%d-%m-%Y')}.csv"
        ),
        mime="text/csv",
        key="download_semua",
    )
else:
  st.caption("Belum ada data kehadiran yang masuk. Yuk isi absen pertama!")
    
