from datetime import datetime
import pandas as pd
import requests
import streamlit as st

# --- 1. KONFIGURASI HALAMAN & TEMA ESTETIK ---
st.set_page_config(
    page_title="Absensi Duta Literasi MTsN 1 Jember",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- 2. CUSTOM CSS (WARNA-WARNI & PASTEL CUTE) ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 50%, #e8eaf6 100%);
        font-family: 'Poppins', sans-serif;
    }
    .main-title {
        color: #ad1457;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #f48fb1, #ce93d8);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ec407a, #ab47bc);
        color: white;
    }
    div.stTextInput>div>div>input, div.stSelectbox>div>div>select, div.stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #f8bbd0;
        background-color: #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 class='main-title'>📚 Absensi Duta Literasi MTsN 1 Jember</h1>",
    unsafe_allow_html=True,
)

# --- 3. KONFIGURASI GOOGLE FORM & SHEETS ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeCb02zXXPpwmd3h-N359jULDITYXflWrZUfFajGSOZFJpQJA/formResponse"
SHEET_ID = "1NIXzAi9Vcb7xIMH5XVQlyJklF8ZorvxYM8Cn_WZcfyw"
CSV_READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"

# --- 4. FORM ABSENSI ---
with st.form("form_absensi", clear_on_submit=True):
  nama = st.text_input("✨ Nama Lengkap")
  status = st.selectbox(
      "📌 Status Kehadiran", ["Hadir", "Izin", "Sakit", "Alpa"]
  )
  karakter = st.text_input("⭐ Karakter / Peran (Opsional)")
  catatan = st.text_area("💬 Catatan (Opsional)")

  submitted = st.form_submit_button("Kirim Absensi 🚀")

  if submitted:
    if not nama.strip():
      st.warning("⚠️ Nama lengkap wajib diisi ya, Kak!")
    else:
      form_data = {
          "entry.1605593113": nama,
          "entry.1825141577": status,
          "entry.1914097499": karakter,
          "entry.1864582280": catatan,
      }
      try:
        response = requests.post(FORM_URL, data=form_data)
        if response.status_code == 200:
          st.success(
              f"✨ Yeay! Absensi **{nama}** berhasil tersimpan cantik ke Google"
              " Sheets!"
          )
        else:
          st.error("Gagal mengirim data. Coba cek kembali koneksi atau form.")
      except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")

# --- 5. REKAP DATA KEHADIRAN ---
st.divider()
st.subheader("📊 Rekap Kehadiran Duta Literasi")

if st.button("🔄 Refresh Data"):
  st.rerun()

try:
  df_rekap = pd.read_csv(CSV_READ_URL)
  if not df_rekap.empty:
    st.dataframe(df_rekap, use_container_width=True)
  else:
    st.info("Belum ada data absensi yang masuk.")
except Exception:
  st.warning(
      "Data rekap belum termuat. Pastikan pengaturan Google Sheets sudah"
      " disetel ke publik (Siapa saja yang memiliki link -> Penglihat)."
  )
