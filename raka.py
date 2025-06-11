import pandas as pd

def loadPertanyaan():
    pertanyaan = pd.read_csv('tb_pertanyaan.csv', delimiter=";")
    pertanyaan.drop('id', inplace=True, axis=1)
    return pertanyaan

def loadRule():
    try:
        rule = pd.read_csv('tb_rule.csv', delimiter=";")
        # Debugging line, Anda bisa hapus setelah memastikan tidak ada masalah 'id' lagi
        # print(f"Kolom yang ditemukan di tb_rule.csv: {rule.columns.tolist()}") 
        
        if 'id' not in rule.columns:
            raise KeyError("Kolom 'id' tidak ditemukan di tb_rule.csv. Mohon periksa header file Anda.")
        
        rule.set_index('id', inplace=True)
        return rule
    except KeyError as e:
        print(f"Error saat memuat tb_rule.csv: {e}.")
        print("Pastikan kolom 'id' ada dan penulisannya benar (huruf kecil, tanpa spasi ekstra).")
        print("Coba buka tb_rule.csv Anda di editor teks biasa untuk memverifikasi header.")
        raise
    except Exception as e:
        print(f"Terjadi error tak terduga saat memuat tb_rule.csv: {e}")
        raise

def getInput(message, response = []):
    if not response:
        return input(message)
    else:
        resok = False
        tempres = None
        while resok is not True:
            tempres = input(message)
            if tempres not in response:
                print("silahkan masukan ","/".join(response))
                resok = False
            else:
                resok = True
        return tempres

if __name__ == "__main__":
    pertanyaan_df = loadPertanyaan()
    rules_df = loadRule()

    checkRule = {}
    for index, row in rules_df.iterrows():
        jurusan_nama = row['jurusan_nama']
        
        gejala_dalam_aturan = {k: v for k, v in row.to_dict().items() if k.startswith('G')}
        
        checkRule[index] = {
            'jurusan_nama': jurusan_nama,
            'gejala_pattern': gejala_dalam_aturan
        }

    print("\nHalo! Saya adalah Do-bot, Saya akan membantu Anda menemukan jurusan yang cocok!")
    print("Silakan jawab pertanyaan berikut (y/t):")
    input("Tekan Enter untuk melanjutkan...")

    resGejala = {}
    minat_terpilih = None
    fakultas_terpilih = None

    # --- Tahap 1: Minat ---
    print("\n--- Tahap 1: Minat ---")
    pertanyaan_minat = pertanyaan_df[pertanyaan_df['tipe_pertanyaan'] == 'minat']

        # Cek apakah ada pertanyaan minat
    if not pertanyaan_minat.empty:
        print("Pilihlah salah satu minat yang paling Anda sukai:")

        # 1. Buat pemetaan dari nomor pilihan ke kategori minat
        pilihan_map = {}
        nomor_pilihan = 1
        for index, row in pertanyaan_minat.iterrows():
            # Tampilkan pilihan ke pengguna
            print(f"  {nomor_pilihan}. {row['gejala'].strip()}")
            # Simpan mapping: kunci adalah nomor (string), nilai adalah kategori
            pilihan_map[str(nomor_pilihan)] = row['kategori_terkait']
            nomor_pilihan += 1

        # 2. Siapkan daftar jawaban yang valid (berdasarkan nomor pilihan)
        jawaban_valid = list(pilihan_map.keys()) # Hasilnya akan seperti ['1', '2', '3']

        # 3. Minta input dari pengguna dan validasi
        pesan_input = f"\nMasukkan pilihan Anda ({'/'.join(jawaban_valid)}): "
        pilihan_pengguna = getInput(pesan_input, jawaban_valid)

        # 4. Tentukan minat terpilih secara langsung dari pilihan pengguna
        if pilihan_pengguna in pilihan_map:
            minat_terpilih = pilihan_map[pilihan_pengguna]

    # Cek hasil dan tampilkan
    if minat_terpilih:
        print(f"\nMinat Anda: {minat_terpilih.upper()}")
    else:
        # Kondisi ini bisa terjadi jika DataFrame pertanyaan_minat kosong
        print("\nTidak ada minat yang dapat diidentifikasi.")


    # --- Tahap 2: Fakultas ---
    print("\n--- Tahap 2: Fakultas ---")
    pertanyaan_fakultas_filtered = pertanyaan_df[pertanyaan_df['tipe_pertanyaan'] == 'fakultas'].copy()

    minat_to_fakultas_map = {
        'saintek': ['teknik', 'teknologi'],
        'sosial': ['hukum', 'psikologi'] 
    }

    if minat_terpilih and minat_terpilih in minat_to_fakultas_map: #minat_terpilih in dst itu cek ada di map atau tidak (line 110,111)
        relevant_fakultas_categories = minat_to_fakultas_map[minat_terpilih] # contoh ['teknik', 'teknologi'] = minat_to_fakultas_map[saintek]
        pertanyaan_fakultas_filtered = pertanyaan_fakultas_filtered[
            pertanyaan_fakultas_filtered['kategori_terkait'].isin(relevant_fakultas_categories) # filter pertanyaan_fakultas_filtered berdasarkan kategori yang relevan
            #contoh: [jurusan yang ada didalam minat saintek] = pertanyaan_fakultas_filtered['kategori_terkait'].isin(['teknik', 'teknologi'])
        ]   #jadi pertanyaan_fakultas_filtered hanya berisi pertanyaan yang relevan dengan minat_terpilih
    else:
        pertanyaan_fakultas_filtered = pd.DataFrame() # Jika minat_terpilih tidak ada di map, pertanyaan_fakultas_filtered menjadi kosong

    if pertanyaan_fakultas_filtered.empty:
        print(f"Tidak ada pertanyaan fakultas yang sesuai dengan minat Anda ('{minat_terpilih}' atau tidak jelas).")
    else:
        print(f"Menampilkan pertanyaan fakultas terkait {minat_terpilih.upper()}:")
        for index, row in pertanyaan_fakultas_filtered.iterrows():
            ans = getInput(f"{row['kode']}. {row['gejala'].strip()} ? ",['y','t'])
            resGejala[row['kode']]=1 if ans.lower() == 'y' else 0
            if ans.lower() == 'y':
                fakultas_terpilih = row['kategori_terkait']
                break # Jika user menjawab 'y', tentukan fakultasnya dan hentikan pertanyaan tahap ini

    # Logika penentuan fakultas terpilih
    # fakultas_scores = {}
    # for kategori_utama in pertanyaan_fakultas_filtered['kategori_terkait'].unique():
    #     relevant_gejala_codes = pertanyaan_fakultas_filtered[pertanyaan_fakultas_filtered['kategori_terkait'] == kategori_utama]['kode'].tolist()
    #     score = sum(resGejala.get(code, 0) for code in relevant_gejala_codes)
    #     total_relevant = len(relevant_gejala_codes)
    #     fakultas_scores[kategori_utama] = score / total_relevant if total_relevant > 0 else 0

    # if fakultas_scores:
    #     fakultas_terpilih_candidate = max(fakultas_scores, key=fakultas_scores.get)
    #     # --- PERBAIKAN 2 ---
    #     if fakultas_scores[fakultas_terpilih_candidate] >= 0.5: # Diubah dari > menjadi >=
    #         fakultas_terpilih = fakultas_terpilih_candidate

    if fakultas_terpilih:
        print(f"\nFakultas yang mungkin cocok: {fakultas_terpilih.upper()}")
    else:
        print("\nTidak ada fakultas yang jelas teridentifikasi atau tidak ada pertanyaan yang relevan.")

    # --- Tahap 3: Jurusan ---
    print("\n--- Tahap 3: Jurusan ---")
    pertanyaan_jurusan_filtered = pertanyaan_df[pertanyaan_df['tipe_pertanyaan'] == 'jurusan'].copy()
    
    fakultas_to_jurusan_map = {
        'teknik': ['arsitektur', 'teknik elektro'],
        'teknologi': ['teknik informatika', 'sistem informasi'],
        'hukum': ['hukum'],
        'psikologi': ['psikologi']
    }

    if fakultas_terpilih and fakultas_terpilih in fakultas_to_jurusan_map:
        relevant_jurusan_categories = fakultas_to_jurusan_map[fakultas_terpilih]
        pertanyaan_jurusan_filtered = pertanyaan_jurusan_filtered[
            pertanyaan_jurusan_filtered['kategori_terkait'].isin(relevant_jurusan_categories)
        ]
    else:
        pertanyaan_jurusan_filtered = pd.DataFrame() 

    if pertanyaan_jurusan_filtered.empty:
        print(f"Tidak ada pertanyaan jurusan yang sesuai dengan fakultas Anda ('{fakultas_terpilih.upper() if fakultas_terpilih else 'tidak jelas'}').")
    else:
        print(f"Menampilkan pertanyaan jurusan terkait {fakultas_terpilih.upper() if fakultas_terpilih else 'umum'}:")
        for index, row in pertanyaan_jurusan_filtered.iterrows():
            ans = getInput(f"{row['kode']}. {row['gejala'].strip()} ? ",['y','t'])
            resGejala[row['kode']]=1 if ans.lower() == 'y' else 0

    # --- Penilaian Kecocokan Jurusan (Exact Match) ---
    print("\n--- Menentukan Jurusan yang Cocok ---")

    fidx_found_rule_data = None
    
    for rule_id, rule_data in checkRule.items():
        rule_gejala_pattern = rule_data['gejala_pattern']
        
        user_gejala_for_this_rule = {kode: resGejala.get(kode, 0) for kode in rule_gejala_pattern.keys()}
        
        if user_gejala_for_this_rule == rule_gejala_pattern:
            fidx_found_rule_data = rule_data
            break

    if fidx_found_rule_data is not None:
        print("\nAnda cocok dengan Jurusan:")
        print(fidx_found_rule_data['jurusan_nama'])
    else:
        print("\nMaaf, tidak ada jurusan yang cocok persis berdasarkan jawaban Anda.")