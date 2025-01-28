import json
import re
import streamlit as st
from langchain.chat_models import ChatOpenAI

# Inisialisasi Streamlit
st.set_page_config(page_title="Food Analyst AI", page_icon="🍜", layout="wide")

# **Deskripsi Aplikasi**
st.markdown("# 🍜 **Food Analyst AI**")
st.markdown("""
**Selamat datang di Food Analyst AI**, asisten cerdas Anda untuk semua kebutuhan makanan! 🎉  
Mulai dari mencari resep lezat, membuat perencanaan makan mingguan, hingga menghitung bahan belanja—semua bisa dilakukan hanya dengan satu aplikasi.  

### ✨ **Apa yang Bisa Dilakukan:**
1. **🔍 Cari Resep Dinamis:** Mencari resep lengkap dengan bahan, langkah, dan estimasi kalori.
2. **📅 Buat Meal Planning Otomatis:** Rencana makan mingguan berdasarkan usia, berat badan, tinggi, tujuan diet, dan preferensi benua.
3. **🔥 Hitung Total Bahan Belanja:** Dapatkan daftar bahan belanja lengkap berdasarkan meal plan.
4. **🧑‍🍳 Konsultasi Teknik Memasak:** Penjelasan langkah-langkah memasak dan tips tambahan.
5. **🌍 Jelajahi Dunia Kuliner:** Temukan makanan dari berbagai benua dengan kalori yang sesuai.

---
""")

# **Collapsible List dengan Expander**
st.markdown("### 💬 **Contoh Pertanyaan yang Bisa Anda Tanyakan:**")

with st.expander("🔍 Cari Resep Dinamis"):
    st.write("- *Berikan resep untuk Ayam Goreng yang sehat.*")
    st.write("- *Bagaimana cara memasak pasta carbonara klasik?*")

with st.expander("📅 Buat Meal Planning Mingguan"):
    st.write("- *Buatkan meal plan untuk pria usia 30 tahun, berat 70 kg, tinggi 170 cm, dengan tujuan menurunkan berat badan dari Asia.*")
    st.write("- *Rencana makan mingguan untuk perempuan 25 tahun yang ingin menambah berat badan.*")

with st.expander("🔥 Hitung Kalori"):
    st.write("- *Berapa kalori dari seporsi nasi goreng udang?*")
    st.write("- *Hitung kalori dari steak ayam dengan saus jamur.*")

with st.expander("🛒 Hitung Total Bahan Belanja"):
    st.write("- *Hitung total bahan makanan yang diperlukan berdasarkan meal plan ini.*")

with st.expander("👨‍🍳 Konsultasi Teknik Memasak"):
    st.write("- *Mengapa ayam perlu dibaluri tepung sebelum digoreng?*")
    st.write("- *Apa teknik terbaik untuk membuat ayam goreng lebih renyah?*")

# Sidebar untuk API Key
st.sidebar.header("🔑 Masukkan OpenAI API Key")
api_key = st.sidebar.text_input("API Key", type="password")
if not api_key:
    st.warning("⚠️ Silakan masukkan OpenAI API Key untuk memulai.")
    st.stop()

# **Sidebar Debugging**
st.sidebar.header("🔍 Debug JSON Output")

# Inisialisasi model ChatGPT dengan gpt-4o-mini
llm_preprocessor = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7)

# **Fungsi Membersihkan JSON**
def clean_and_parse_json(response):
    try:
        response = response.strip()

        # Deteksi jika respons tidak berupa JSON
        if not response.startswith("{") and not response.startswith("["):
            return None, response

        response = re.sub(r"```json\n|\n```", "", response.strip())

        # Debugging Output JSON di Sidebar
        st.sidebar.write("📝 **Cleaned JSON Output:**")
        st.sidebar.json(response)

        return json.loads(response), None

    except json.JSONDecodeError:
        st.sidebar.error("⚠️ Respons yang diterima bukan format JSON yang valid.")
        return None, response

# **Fungsi untuk Menghasilkan Meal Planning**
def generate_dynamic_meal_plan(age, weight, height, goal, continent):
    prompt = f"""
    Anda adalah ahli nutrisi. Buatkan rencana makan mingguan yang sehat berdasarkan informasi berikut:
    - Usia: {age} tahun
    - Berat badan: {weight} kg
    - Tinggi badan: {height} cm
    - Tujuan diet: {goal}
    - Preferensi makanan: makanan dari benua {continent}

    Rencana makan harus mencakup sarapan, makan siang, dan makan malam untuk 7 hari.
    """
    response = llm_preprocessor.predict(prompt)
    return response

# **Fungsi untuk Menghitung Total Bahan Belanja**
def calculate_total_shopping(meal_plan):
    prompt = f"""
    Berdasarkan rencana makan berikut, buatkan daftar total bahan makanan yang dibutuhkan (dengan satuan) untuk 7 hari.
    Gabungkan jumlah bahan yang sama.

    Rencana makan:
    {meal_plan}

    Output harus berupa JSON dengan struktur:
    {{
        "Bahan": [
            {{
                "Nama": "Nama Bahan",
                "Jumlah": "Jumlah dengan Satuan"
            }},
            ...
        ]
    }}
    """
    response = llm_preprocessor.predict(prompt)
    parsed_json, fallback_text = clean_and_parse_json(response)

    if parsed_json:
        return parsed_json["Bahan"]
    else:
        return fallback_text

# **Fungsi Utama**
def process_user_request(user_input):
    response = llm_preprocessor.predict(user_input)
    parsed_json, fallback_text = clean_and_parse_json(response)

    if parsed_json:
        maksud = parsed_json.get("Maksud")
        data = parsed_json.get("Data", [])

        if maksud == "buat_meal_plan":
            return generate_dynamic_meal_plan(data[0], data[1], data[2], data[3], data[4])
        elif maksud == "hitung_total_belanja":
            return calculate_total_shopping(data[0])
    else:
        return fallback_text

# **Tampilan Chat**
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("Tanyakan sesuatu pada Food Analyst AI:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Memahami maksud Anda..."):
        response = process_user_request(user_input)

        with st.chat_message("ai"):
            st.markdown("🤖 **Food Analyst AI**")
            if isinstance(response, list):  # Jika hasilnya daftar belanja
                st.write("### 🛒 Total Bahan Belanja:")
                for item in response:
                    st.write(f"- {item['Nama']}: {item['Jumlah']}")
            else:  # Teks respons biasa
                st.write(response)

        st.session_state.messages.append({"role": "ai", "content": response})
