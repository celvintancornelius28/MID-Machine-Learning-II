import streamlit as st
import pandas as pd
import joblib

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="IoT Vulnerability IDS",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# 2. FUNGSI LOAD ARTIFACT PIPELINE
# ==========================================
# st.cache_resource digunakan agar model hanya di-load 1 kali di memori (tidak berulang-ulang)
@st.cache_resource
def load_model():
    # Memuat objek Pipeline utuh (Scaler -> Feature Selection -> Model)
    pipeline = joblib.load('pipeline_terbaik.pkl')
    return pipeline

pipeline_model = load_model()

# ==========================================
# 3. ANTARMUKA PENGGUNA (UI) UTAMA
# ==========================================
st.title("🛡️ Sistem Deteksi Kerentanan IoT (IoT Vulnerability IDS)")
st.markdown("""
Aplikasi ini mendemonstrasikan kapabilitas Machine Learning dalam mendeteksi dan mengklasifikasikan 
serangan siber pada lalu lintas jaringan *Internet of Things* (IoT).
""")
st.markdown("---")

# ==========================================
# 4. SIDEBAR (PANEL UNGGAH DATA)
# ==========================================
st.sidebar.header("📂 Panel Input Data")
st.sidebar.write("Silakan unggah rekaman data trafik jaringan (format .csv).")

uploaded_file = st.sidebar.file_uploader("Pilih file CSV", type=["csv"])

# ==========================================
# 5. LOGIKA PREDIKSI & VISUALISASI
# ==========================================
if uploaded_file is not None:
    try:
        # Membaca data yang diunggah
        df_input = pd.read_csv(uploaded_file)
        
        st.write("### 🔍 Pratinjau Data Input (Raw Data)")
        st.dataframe(df_input.head())
        
        # Tombol eksekusi
        if st.button("🚀 Jalankan Deteksi Anomali", type="primary"):
            with st.spinner("Memproses data melalui Pipeline (Scaling & Ekstraksi Fitur)..."):
                
                # CATATAN: Jika dataset yang diunggah masih memiliki kolom target di akhir, 
                # kita harus menghapusnya agar fitur sesuai dengan saat training (87 kolom).
                if len(df_input.columns) == 88:
                    X_input = df_input.iloc[:, :-1]
                else:
                    X_input = df_input
                
                # Eksekusi prediksi (Pipeline otomatis melakukan transform scaler dan feature selection)
                predictions = pipeline_model.predict(X_input)
                
                # ---------------------------------------------------------
                # KAMUS PEMETAAN (LABEL DECODING)
                # ---------------------------------------------------------
                kamus_serangan = {
                    0: 'ARPPoisoning',
                    1: 'Backdoor',
                    2: 'ICMPflood',
                    3: 'ICMPredirect',
                    4: 'Normal',
                    5: 'Password_crack',
                    6: 'Port_Scanning',
                    7: 'SQLInjection',
                    8: 'SYN_FLOOD',
                    9: 'Smurf',
                    10: 'UDP_flood',
                    11: 'VUlnerability_Scan'
                }
                
                # Mengubah hasil prediksi (angka) menjadi nama serangan (teks)
                prediksi_teks = [kamus_serangan.get(angka, f"Unknown ({angka})") for angka in predictions]
                
                # Menggabungkan hasil prediksi ke dalam dataframe asli untuk ditampilkan
                df_hasil = X_input.copy()
                df_hasil['🔥 Kategori_Deteksi'] = prediksi_teks
                
                st.success("✅ Analisis Jaringan Selesai!")
                
                st.write("### 📊 Hasil Klasifikasi Serangan")
                # Menampilkan data dengan highlight pada kolom hasil deteksi
                st.dataframe(df_hasil.style.highlight_max(subset=['🔥 Kategori_Deteksi'], color='red'))
                
                # Menampilkan rangkuman deteksi
                st.write("### 📋 Rangkuman Aktivitas Jaringan")
                ringkasan = df_hasil['🔥 Kategori_Deteksi'].value_counts().reset_index()
                ringkasan.columns = ['Kategori / Jenis Serangan', 'Jumlah Paket Terdeteksi']
                st.table(ringkasan)
                
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat memproses data: {e}")
        st.info("Pastikan file CSV yang diunggah memiliki struktur 87 fitur prediktor yang sama dengan dataset latih.")
else:
    st.info("Menunggu data... Silakan unggah file CSV melalui panel di sebelah kiri untuk memulai demonstrasi.")