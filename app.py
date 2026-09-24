import streamlit as st
import pandas as pd
import numpy as np
import io

# Konfigurasi Tampilan Halaman
st.set_page_config(page_title="SPK MOORA - Pemilihan Kendaraan Operasional", layout="wide")

st.title("🚚 SPK Pemilihan Kendaraan Operasional Lapangan")
st.caption("Aplikasi Sistem Pendukung Keputusan Metode MOORA untuk Perusahaan Distribusi")

# 1. Inisialisasi Data Awal (Session State)
if 'kriteria' not in st.session_state:
    st.session_state.kriteria = pd.DataFrame([
        {"Kode": "C1", "Nama": "Harga Beli (Rp Juta)", "Bobot": 0.25, "Jenis": "Cost"},
        {"Kode": "C2", "Nama": "Konsumsi BBM (Liter/100km)", "Bobot": 0.25, "Jenis": "Cost"},
        {"Kode": "C3", "Nama": "Kapasitas Muatan (Kg)", "Bobot": 0.20, "Jenis": "Benefit"},
        {"Kode": "C4", "Nama": "Biaya Perawatan (Rp Juta/Thn)", "Bobot": 0.15, "Jenis": "Cost"},
        {"Kode": "C5", "Nama": "Jaringan Servis (Skala 1-5)", "Bobot": 0.15, "Jenis": "Benefit"}
    ])

if 'alternatif' not in st.session_state:
    st.session_state.alternatif = pd.DataFrame([
        {"Kode": "A1", "Nama": "Toyota Hilux SC", "C1": 300.0, "C2": 8.5, "C3": 1000.0, "C4": 6.5, "C5": 5.0},
        {"Kode": "A2", "Nama": "Isuzu Traga PU", "C1": 260.0, "C2": 7.0, "C3": 1500.0, "C4": 5.0, "C5": 4.0},
        {"Kode": "A3", "Nama": "Mitsubishi L300", "C1": 240.0, "C2": 7.5, "C3": 1200.0, "C4": 4.5, "C5": 5.0},
        {"Kode": "A4", "Nama": "Daihatsu Gran Max", "C1": 170.0, "C2": 6.0, "C3": 800.0, "C4": 3.5, "C5": 4.0},
        {"Kode": "A5", "Nama": "Suzuki Carry PU", "C1": 165.0, "C2": 5.8, "C3": 800.0, "C4": 3.2, "C5": 4.0}
    ])

# 2. Sidebar Navigasi
menu = st.sidebar.radio("Navigasi Menu", [
    "Informasi SPK", 
    "Data Kriteria", 
    "Data Alternatif & Matriks", 
    "Proses MOORA & Hasil Ranking", 
    "Ekspor Laporan"
])

# MENU 1: INFORMASI SPK
if menu == "Informasi SPK":
    st.header("📌 Informasi & Konsep SPK")
    st.markdown("""
    Aplikasi ini dirancang untuk membantu **Perusahaan Distribusi** dalam memilih kendaraan operasional lapangan terbaik menggunakan metode **MOORA (Multi-Objective Optimization on the basis of Ratio Analysis)**.
    
    **Komponen Utama SPK:**
    * **Data Subsystem:** Pengelolaan kriteria, bobot, dan data alternatif.
    * **Model Subsystem:** Algoritma pemrosesan metode MOORA.
    * **Dialog Subsystem:** Antarmuka interaktif berbasis web Streamlit.
    """)

# MENU 2: DATA KRITERIA
elif menu == "Data Kriteria":
    st.header("⚙️ Pengelolaan Data Kriteria & Bobot")
    st.info("Anda dapat mengubah bobot dan jenis kriteria secara langsung pada tabel di bawah ini.")
    
    edited_kriteria = st.data_editor(st.session_state.kriteria, num_rows="dynamic")
    
    total_bobot = edited_kriteria['Bobot'].sum()
    if not np.isclose(total_bobot, 1.0):
        st.warning(f"⚠️ Total bobot saat ini: **{total_bobot:.2f}**. Pastikan total bobot bernilai **1.00**.")
    else:
        st.success("✅ Total bobot sudah bernilai pas 1.00.")
    
    st.session_state.kriteria = edited_kriteria

# MENU 3: DATA ALTERNATIF
elif menu == "Data Alternatif & Matriks":
    st.header("📋 Matriks Keputusan Alternatif")
    st.info("Anda dapat menambah, menghapus, atau mengedit data nilai alternatif.")
    
    edited_alt = st.data_editor(st.session_state.alternatif, num_rows="dynamic")
    st.session_state.alternatif = edited_alt

# MENU 4: PROSES MOORA & RANKING
elif menu == "Proses MOORA & Hasil Ranking":
    st.header("🧮 Hitung Metode MOORA")
    
    df_alt = st.session_state.alternatif.copy()
    df_krit = st.session_state.kriteria.copy()
    
    criterion_cols = df_krit['Kode'].tolist()
    matrix = df_alt[criterion_cols].to_numpy(dtype=float)
    
    # Langkah 1: Matriks Normalisasi
    divisors = np.sqrt(np.sum(matrix**2, axis=0))
    normalized_matrix = matrix / divisors
    
    df_norm = df_alt[['Kode', 'Nama']].copy()
    for i, col in enumerate(criterion_cols):
        df_norm[col] = normalized_matrix[:, i]
        
    st.subheader("1. Matriks Normalisasi (R)")
    st.dataframe(df_norm, use_container_width=True)
    
    # Langkah 2: Optimalisasi & Pengbobotan
    weights = df_krit['Bobot'].to_numpy(dtype=float)
    weighted_matrix = normalized_matrix * weights
    
    types = df_krit['Jenis'].tolist()
    benefit_idx = [i for i, t in enumerate(types) if t == "Benefit"]
    cost_idx = [i for i, t in enumerate(types) if t == "Cost"]
    
    sum_benefit = np.sum(weighted_matrix[:, benefit_idx], axis=1) if benefit_idx else np.zeros(len(df_alt))
    sum_cost = np.sum(weighted_matrix[:, cost_idx], axis=1) if cost_idx else np.zeros(len(df_alt))
    
    yi = sum_benefit - sum_cost
    
    # Langkah 3: Hasil Ranking
    df_result = df_alt[['Kode', 'Nama']].copy()
    df_result['Nilai Max (Benefit)'] = sum_benefit
    df_result['Nilai Min (Cost)'] = sum_cost
    df_result['Nilai Akhir (Yi)'] = yi
    df_result['Ranking'] = df_result['Nilai Akhir (Yi)'].rank(ascending=False, method='min').astype(int)
    df_result = df_result.sort_values(by='Ranking')
    
    st.subheader("2. Hasil Ranking Keputusan")
    st.dataframe(df_result, use_container_width=True)
    
    # Rekomendasi Naratif
    best_alt = df_result.iloc[0]
    st.success(f"🏆 **Rekomendasi Utama:** Keputusan terbaik jatuh pada **{best_alt['Nama']} ({best_alt['Kode']})** dengan Nilai Akhir (Yi) sebesar **{best_alt['Nilai Akhir (Yi)']:.4f}**.")
    st.write(f"**Analisis Keputusan:** Alternatif **{best_alt['Nama']}** terpilih karena memiliki kombinasi efisiensi biaya operasional dan kapasitas yang paling menguntungkan sesuai bobot kriteria perusahaan.")

# MENU 5: EKSPOR LAPORAN
elif menu == "Ekspor Laporan":
    st.header("📄 Unduh Laporan LENGKAP")
    
    # Kalkulasi ulang untuk ekspor
    df_alt = st.session_state.alternatif.copy()
    df_krit = st.session_state.kriteria.copy()
    criterion_cols = df_krit['Kode'].tolist()
    matrix = df_alt[criterion_cols].to_numpy(dtype=float)
    divisors = np.sqrt(np.sum(matrix**2, axis=0))
    normalized_matrix = matrix / divisors
    weights = df_krit['Bobot'].to_numpy(dtype=float)
    weighted_matrix = normalized_matrix * weights
    types = df_krit['Jenis'].tolist()
    benefit_idx = [i for i, t in enumerate(types) if t == "Benefit"]
    cost_idx = [i for i, t in enumerate(types) if t == "Cost"]
    sum_benefit = np.sum(weighted_matrix[:, benefit_idx], axis=1) if benefit_idx else np.zeros(len(df_alt))
    sum_cost = np.sum(weighted_matrix[:, cost_idx], axis=1) if cost_idx else np.zeros(len(df_alt))
    yi = sum_benefit - sum_cost
    
    df_export = df_alt[['Kode', 'Nama']].copy()
    df_export['Nilai Akhir (Yi)'] = yi
    df_export['Ranking'] = df_export['Nilai Akhir (Yi)'].rank(ascending=False, method='min').astype(int)
    df_export = df_export.sort_values(by='Ranking')
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Hasil Ranking MOORA', index=False)
        df_krit.to_excel(writer, sheet_name='Data Kriteria', index=False)
        df_alt.to_excel(writer, sheet_name='Data Alternatif', index=False)
    
    st.download_button(
        label="📥 Download Laporan (Excel)",
        data=buffer.getvalue(),
        file_name="Laporan_Hasil_SPK_MOORA.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )