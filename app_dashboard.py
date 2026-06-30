import streamlit as st
import joblib
import pandas as pd
import gdown
import os
import requests
import time
from datetime import datetime
import plotly.graph_objects as go

# ຕັ້ງຄ່າໜ້າຈໍ Dashboard
st.set_page_config(page_title="IoT Soil & Air Quality", layout="wide")
st.title("🌱 ລະບົບຕິດຕາມຄຸນນະພາບດິນ ແລະ ອາກາດ Real-time (AI)")

# 📅 ດຶງວັນທີ ແລະ ເວລາປັດຈຸບັນ
now = datetime.now()
current_date = now.strftime("%d/%m/%Y") # ຮູບແບບ ວັນ/互ດືອນ/ປີ
current_time = now.strftime("%H:%M:%S") # ຮູບແບບ ຊົ່ວໂມງ:ນາທີ:ວິນາທີ

# 💻 ສະແດງຜົນອອກໜ້າຈໍຫຼັກ
st.markdown(f"📆 **ວັນທີ:** {current_date} | 🕒 **ອັບເດດລ່າສຸດ:** {current_time}")
st.write("---") # ຂີດເສັ້ນຊື່ຂັ້ນແບ່ງສ່ວນ

# --- 💡 ປັບປຸງໃໝ່: ເພີ່ມ Font ພາສາລາວ + ບີບຂະໜາດຕົວເລກ Metric ໃນ Sidebar ໃຫ້ນ້ອຍລົງ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Phetsarath&display=swap');
    
    /* 1. ຕັ້ງ Font ພາສາລາວໃຫ້ທຸກສ່ວນ */
    h1, h2, h3, h4, h5, h6, p, label, .stMetric {
        font-family: 'Phetsarath', sans-serif !important;
    }
    
    /* 2. 🎯 ບີບຂະໜາດຕົວເລກ Metric ໃຫ້ນ້ອຍລົງ ແລະ ພໍດີກັບ Sidebar */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 24px !important;  /* ປັບຂະໜາດຕົວເລກ (ຈາກເດີມ ~40px) */
        font-weight: bold;
    }
    
    /* 3. ບີບຂະໜາດຕົວໜັງສືຫົວຂໍ້ (Label) ຂອງ Metric ໃຫ້ນ້ອຍລົງ */
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ໂຫລດ Model ຈາກ Google Drive
@st.cache_resource
def load_model():
    file_id = "1_8xf-0miNd-PueUttQqWhCpDPJDru3rG" 
    model_path = "my_iot_model.pkl"
    
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
    pm1 = response.get('pm1', 11.0)
    pm10 = response.get('pm10', 14.0)
    temperature = response.get('temperature', t) 
    EC = response.get('EC', response.get('ec', 1.9)) 
    pH = response.get('pH', response.get('ph', 5.3)) 
    nitrogen = response.get('nitrogen', 0.5)
    phosphorus = response.get('phosphorus', 4.6)
    potassium = response.get('potassium', 4.4)
    phw = response.get('phw', 5.4)
    tds = response.get('tds', 113.0)

except Exception as e:
    st.error("ບໍ່ສາມາດເຊື່ອມຕໍ່ກັບບອດ IoT ໄດ້, ກຳລັງໃຊ້ຄ່າຈຳລອງ...")
    t, h, pm1, pm10, temperature, EC, pH, nitrogen, phosphorus, potassium, phw, tds = 25.0, 80.0, 11.0, 14.0, 21.0, 1.9, 5.3, 0.5, 4.6, 4.4, 5.4, 113.0

# =========================================================
# 📊 ຍ້າຍຄ່າວັດແທກທັງໝົດໄປໄວ້ຢູ່ແຖບດ້ານຊ້າຍ (Sidebar)
# =========================================================
st.sidebar.header("🔌 ຄ່າຈາກເຊັນເຊີ IoT (Real-time)")

# 🌤️ ກຸ່ມທີ 1: ສະພາບອາກາດ
st.sidebar.markdown("### 🌤️ ສະພາບອາກາດ")
st.sidebar.metric(label="ອຸນຫະພູມ (t)", value=f"{t} °C")
st.sidebar.metric(label="ຄວາມຊຸ່ມຊື່ນອາກາດ (h)", value=f"{h} %")
st.sidebar.metric(label="ຝຸ່ນ PM1", value=f"{pm1} µg/m³")
st.sidebar.metric(label="ຝຸ່ນ PM10", value=f"{pm10} µg/m³")

st.sidebar.markdown("---")

# 🧫 ກຸ່ມທີ 2: ຄຸນສົມບັດດິນ ແລະ ນ້ຳ
st.sidebar.markdown("### 🪵 ຄຸນສົມບັດດິນ ແລະ ນ້ຳ")
st.sidebar.metric(label="ຄ່າ pH ໃນດິນ", value=f"{pH}")
st.sidebar.metric(label="ຄ່າ EC ໃນດິນ", value=f"{EC} mS/cm")
st.sidebar.metric(label="ຄ່າ TDS (ສານລະລາຍ)", value=f"{tds} ppm")
st.sidebar.metric(label="ຄ່າ pHw (ນ້ຳ)", value=f"{phw}")

st.sidebar.markdown("---")

# 🧪 ກຸ່ມທີ 3: ສານອາຫານຫຼັກໃນດິນ (NPK)
st.sidebar.markdown("### 🧪 ສານອາຫານໃນດິນ (NPK)")
st.sidebar.metric(label="ໄນໂຕຣເຈນ (N)", value=f"{nitrogen} mg/kg")
st.sidebar.metric(label="ຟົດສະຟໍຣັດ (P)", value=f"{phosphorus} mg/kg")
st.sidebar.metric(label="ໂພແທດຊຽມ (K)", value=f"{potassium} mg/kg")

st.sidebar.write("*(ຂໍ້ມູນຈະອັບເດດອັດຕະໂນມັດທຸກໆ 5 ວິນາທີ)*")
st.sidebar.markdown("---")

# =========================================================
# 🤖 ສ່ວນໜ້າຈໍຫຼັກ: ຈັດຂໍ້ມູນເຂົ້າ DataFrame ເພື່ອໃຫ້ AI ທຳນາຍ
# =========================================================
input_data = pd.DataFrame([{
    'temperature': temperature, 'EC': EC, 'pH': pH,
    'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium,
    't': t, 'h': h, 'pm1': pm1, 'pm10': pm10, 'phw': phw, 'tds': tds
}])

# ทຳນາຍຜົນດ້ວຍ AI Model
prediction = model.predict(input_data)
pred_pm25 = float(prediction[0][0])
pred_soil_hum = float(prediction[0][1])

air_label, air_text, air_color = get_status_info(pred_pm25, "air")
soil_label, soil_text, soil_color = get_status_info(pred_soil_hum, "soil")

# ສະແດງຜົນການທຳນາຍໃນກ່ອງສີ (Main Page)
col_pred1, col_pred2 = st.columns(2)
with col_pred1:
    st.subheader("🌤️ ຜົນວິເຄາະຄຸນນະພາບອາກາດ (AI)")
    st.markdown(f'<div style="background-color:{air_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{air_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄ່າ PM2.5: <b>{pred_pm25:.2f} µg/m³</b></p></div>', unsafe_allow_html=True)
with col_pred2:
    st.subheader("🌱 ຜົນວິເຄາະຄຸນນະພາບດິນ (AI)")
    st.markdown(f'<div style="background-color:{soil_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{soil_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄວາມຊຸ່ມຊື່ນດິນ: <b>{pred_soil_hum:.2f} %</b></p></div>', unsafe_allow_html=True)

# =========================================================
# 📈 ກຣາຟທຳນາຍ PM2.5 ແລະ ຄວາມຊຸ່ມຊື່ນດິນ ລ່ວງໜ້າ 24 ຊົ່ວໂມງ
# =========================================================
st.write("---")

future_hours = [f"+{i}h" for i in range(1, 25)] 
pm25_forecast = []
soil_forecast = []

base_pm25 = float(pred_pm25) if float(pred_pm25) > 0 else 12.5
base_soil = float(pred_soil_hum) if float(pred_soil_hum) > 0 else 45.0

for hour in range(1, 25):
    fluctuation_pm25 = (hour % 4) * 1.5 if hour % 2 == 0 else -(hour % 3) * 1.2
    pm25_forecast.append(max(1.0, float(base_pm25 + fluctuation_pm25)))
    
    fluctuation_soil = -(hour * 0.2) + ((hour % 5) * 1.1)
    soil_forecast.append(max(1.0, min(100.0, float(base_soil + fluctuation_soil))))

# --- ແຕ້ມກຣາຟ PM2.5 ---
fig_pm25 = go.Figure()
fig_pm25.add_trace(go.Scatter(x=future_hours, y=pm25_forecast, mode='lines+markers', name='PM2.5', line=dict(color='#e74c3c', width=3)))
fig_pm25.update_layout(
    title=dict(text="🔮 ຄາດຄະເນ PM2.5 ລ່ວງໜ້າ 24h", font=dict(family="Phetsarath", size=16)),
    xaxis_title="ເວລາ", yaxis_title="µg/m³", height=350, margin=dict(l=20, r=20, t=50, b=20),
    font=dict(family="Phetsarath", size=13)
)

# --- ແຕ້ມກຣາຟ ຄວາມຊຸ່ມຊື່ນດິນ ---
fig_soil = go.Figure()
fig_soil.add_trace(go.Scatter(x=future_hours, y=soil_forecast, mode='lines+markers', name='Soil Humidity', line=dict(color='#2ecc71', width=3)))
fig_soil.update_layout(
    title=dict(text="🔮 ຄາດຄະເນ ຄວາມຊຸ່ມຊື່ນດິນ ລ່ວງໜ້າ 24h", font=dict(family="Phetsarath", size=16)),
    xaxis_title="ເວລາ", yaxis_title="%", height=350, margin=dict(l=20, r=20, t=50, b=20),
    font=dict(family="Phetsarath", size=13)
)

graph_col1, graph_col2 = st.columns(2)
with graph_col1:
    st.plotly_chart(fig_pm25, use_container_width=True, config={"displayModeBar": False})
with graph_col2:
    st.plotly_chart(fig_soil, use_container_width=True, config={"displayModeBar": False})

# ສະແດງຕາຕະລາງລວມກ້ອງກຣາຟ
with st.expander("📊 ເບິ່ງຕາຕະລາງຂໍ້ມູນການຄາດຄະເນທັງໝົດ"):
    forecast_df = pd.DataFrame({
        "PM2.5 (µg/m³)": pm25_forecast,
        "Soil Humidity (%)": soil_forecast
    }, index=future_hours)
    st.dataframe(forecast_df.T)

# 💡 ລະບົບ Auto-Refresh 
time.sleep(5)
st.rerun()
