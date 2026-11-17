import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Absensi Duta Literasi MTsN 1 Jember",
    page_icon="📚",
    layout="centered",
)

st.title("📚 Absensi Duta Literasi MTsN 1 Jember")

# Konfigurasi Google Form & Google Sheets
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeCb02zXXPpwmd3h-N359jULDITYXflWrZUfFajGSOZFJpQJA/formResponse"
SHEET_ID = "1NIXzAi9Vcb7xIMH5XVQlyJklF8ZorvxYM8Cn_WZcfyw"
# Tab hasil Google Form otomatis bernama 'Form Responses 1'
CSV_READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"

# --- FORM ABSENSI ---
with st.form("form_absensi", clear_on_submit=True):
  nama = st.text_input("Nama Lengkap")
  status = st.selectbox("Status Kehadiran", ["Hadir", "Izin", "Sakit", "Alpa"])
  karakter = st.text_input("Karakter / Peran (Opsional)")
  catatan = st.text_area("Catatan (Opsional)")

  submitted = st.form_submit_button("Kirim Absensi")

  if submitted:
    if nama.strip() == "":
      st.warning("⚠️ Nama lengkap wajib diisi ya!")
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
              f"✅ Mantap! Absensi **{nama}** berhasil tersimpan ke Google"
              " Sheets!"
          )
        else:
          st.error(
              "Gagal mengirim data. Pastikan Google Form sudah di-Publikasikan"
              " untuk umum."
          )
      except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")

# --- REKAP DATA KEHADIRAN ---
st.divider()
st.subheader("📊 Rekap Kehadiran (Semua Data)")

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
      "Data belum bisa ditampilkan. Pastikan Google Sheets sudah diatur ke"
      " 'Siapa saja yang memiliki link -> Penglihat'."
  )
