import streamlit as st
import joblib
import pandas as pd
import gdown
import os
import requests
import time
from datetime import datetime

# ຕັ້ງຄ່າໜ້າຈໍ Dashboard
st.set_page_config(page_title="IoT Soil & Air Quality", layout="wide")
st.title("🌱 ລະບົບຕິດຕາມຄຸນນະພາບດິນ ແລະ ອາກາດ Real-time (AI)")

# --- ເພີ່ມ Font ພາສາລາວ (ສະບັບຕັດຕົວບັນຫາອອກເພື່ອຄວາມຊົວຣ໌) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Phetsarath&display=swap');

    /* ປ່ຽນຟອນສະເພາະຂໍ້ຄວາມ ແລະ ຫົວຂໍ້ເທົ່ານັ້ນ (ບໍ່ໃຫ້ໄປແຕະຕ້ອງ class ຂອງລະບົບ) */
    h1, h2, h3, h4, h5, h6, p, label, .stMetric {
        font-family: 'Phetsarath', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ໂຫລດ Model ຈາກ Google Drive (ເພີ່ມລະບົບດາວໂຫລດອັດຕະໂນມັດ)
@st.cache_resource
def load_model():
    # ⚠️ ເອົາ ID ໄຟລ໌ Google Drive ຂອງທ່ານມາປ່ຽນໃສ່ບ່ອນນີ້ເດີ້
    file_id = "1_8xf-0miNd-PueUttQqWhCpDPJDru3rG" 
    model_path = "my_iot_model.pkl"
    
    # ຖ້າໃນເຊີເວີຍັງບໍ່ມີໄຟລ໌ model ໃຫ້ດາວໂຫລດມາທັນທີ
    if not os.path.exists(model_path):
        with st.spinner("ກຳລັງໂຫລດ AI Model ຈາກ Google Drive... ກະລຸນາຖ້າ"):
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, model_path, quiet=False)
            
    return joblib.load(model_path)

model = load_model()

# ຟັງຊັນຈັດກຸ່ມ (Good, Moderate, Poor)
def get_status_info(value, metric_type):
    if metric_type == "air":
        if value <= 12: return "Good", "🟢 ດີຫຼາຍ", "#2ecc71"
        elif value <= 14: return "Moderate", "🟡 ປານກາງ", "#f1c40f"
        else: return "Poor", "🔴 ບໍ່ດີ (ອັນຕະລາຍ)", "#e74c3c"
    elif metric_type == "soil":
        if value < 20: return "Poor", "🔴 ແຫ້ງແລ້ງເກີນໄປ", "#e74c3c"
        elif value <= 40: return "Moderate", "🟡 ປານກາງ", "#f1c40f"
        else: return "Good", "🟢 ຊຸ່ມຊື່ນດີ", "#2ecc71"

# --- ສ່ວນດຶງຂໍ້ມູນ Real-time ຈາກ Firebase ---
FIREBASE_URL = "https://my-iot-project-5432f-default-rtdb.asia-southeast1.firebasedatabase.app/iot_data.json"

try:
    # ດຶງຂໍ້ມູນຈາກ Firebase
    response = requests.get(FIREBASE_URL).json()
    
    # ແຍກຂໍ້ມູນອອກມາ (ຖ້າ Firebase ຍັງບໍ່ມີຂໍ້ມູນ ໃຫ້ໃຊ້ຄ່າ Default ແທນ)
    t = response.get('t', 25.0)
    h = response.get('h', 80.0)
    pm1 = response.get('pm1', 11)
    pm10 = response.get('pm10', 14)
    temperature = response.get('temperature', 21.0)
    EC = response.get('EC', 1.9)
    pH = response.get('pH', 5.3)
    nitrogen = response.get('nitrogen', 0.5)
    phosphorus = response.get('phosphorus', 4.6)
    potassium = response.get('potassium', 4.4)
    phw = response.get('phw', 5.4)
    tds = response.get('tds', 113.0)

except Exception as e:
    st.error("ບໍ່ສາມາດເຊື່ອມຕໍ່ກັບບອດ IoT ໄດ້, ກຳລັງໃຊ້ຄ່າຈຳລອງ...")
    # ຄ່າ Default ຖ້າດຶງຂໍ້ມູນບໍ່ໄດ້
    t, h, pm1, pm10, temperature, EC, pH, nitrogen, phosphorus, potassium, phw, tds = 25.0, 80.0, 11, 14, 21.0, 1.9, 5.3, 0.5, 4.6, 4.4, 5.4, 113.0
# ສະແດງວັນທີຢູ່ Sidebar
now = datetime.now()
st.sidebar.markdown(f"📅 **ວັນທີ:** {now.strftime('%d/%m/%Y')} | 🕒 **ເວລາ:** {now.strftime('%H:%M:%S')}")
st.sidebar.write("---")
# ສະແດງຄ່າປັດຈຸບັນທີ່ໄດ້ຈາກ IoT ຢູ່ Sidebar (ປ່ຽນຈາກ Slider ເປັນການໂຊຕົວເລກ)
st.sidebar.header("🔌 ຄ່າຈາກເຊັນເຊີ IoT (Real-time)")
st.sidebar.metric("ອຸນຫະພູມອາກາດ (t)", f"{t} °C")
st.sidebar.metric("ຄວາມຊຸ່ມຊື່ນອາກາດ (h)", f"{h} %")
st.sidebar.metric("ຄ່າ pH ໃນດິນ", f"{pH}")
st.sidebar.metric("ຄ່າ EC ໃນດິນ", f"{EC} mS/cm")
st.sidebar.write("*(ຂໍ້ມູນຈະອັບເດດອັດຕະໂນມັດທຸກໆ 10 ວິນາທີ)*")

# ຈັດຂໍ້ມູນໃສ່ DataFrame ເພື່ອທຳນາຍ
input_data = pd.DataFrame([{
    'temperature': temperature, 'EC': EC, 'pH': pH,
    'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium,
    't': t, 'h': h, 'pm1': pm1, 'pm10': pm10, 'phw': phw, 'tds': tds
}])

# ທຳນາຍຜົນ
prediction = model.predict(input_data)
pred_pm25 = float(prediction[0][0])
pred_soil_hum = float(prediction[0][1])

air_label, air_text, air_color = get_status_info(pred_pm25, "air")
soil_label, soil_text, soil_color = get_status_info(pred_soil_hum, "soil")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🌤️ ຄຸນນະພາບອາກາດ")
    st.markdown(f'<div style="background-color:{air_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{air_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄ່າ PM2.5: <b>{pred_pm25:.2f} µg/m³</b></p></div>', unsafe_allow_html=True)
with col2:
    st.subheader("🌱 ຄຸນນະພາບດິນ")
    st.markdown(f'<div style="background-color:{soil_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{soil_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄວາມຊຸ່ມຊື່ນດິນ: <b>{pred_soil_hum:.2f} %</b></p></div>', unsafe_allow_html=True)

# 💡 ເພີ່ມລະບົບ Auto-Refresh ເພື່ອໃຫ້ໜ້າເວັບໂຫຼດຂໍ້ມູນໃໝ່ທຸກໆ 10 ວິນາທີ
time.sleep(10)
st.rerun()
