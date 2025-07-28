import streamlit as st
import pandas as pd
import datetime
import os
import requests
from dotenv import load_dotenv
from predict import predict_irrigation
from utils.fertilizer import suggest_fertilizer
from sms_alert import send_sms_alert
from gtts import gTTS

import os

# ✅ Ensure 'data/' folder exists
if not os.path.exists("data"):
    os.makedirs("data")


# ==== 🌍 Load Environment Variables ====
load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="Smart Agriculture", layout="centered")
st.title("🌾 Smart Agriculture Dashboard")

# ==== Weather API Function ====
def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200:
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return temp, humidity
    else:
        return None, None

# ==== 📤 Upload Dataset ====
st.subheader("📤 Upload Your Sensor Data (CSV)")
uploaded_file = st.file_uploader("Choose CSV file", type="csv")
if uploaded_file:
    df_new = pd.read_csv(uploaded_file)
    df_new.to_csv("data/sensor_data.csv", index=False, mode="a", header=False)
    st.success("✅ Data uploaded successfully!")

# ==== 🗑️ Delete Data Option ====
if st.button("🗑️ Clear All Sensor Data"):
    open("data/sensor_data.csv", "w").close()
    st.success("✅ All data cleared.")

# ==== 🌤️ Weather API Input ====
st.subheader("🌤️ Get Weather Data from City")
city = st.text_input("Enter City Name", "Hyderabad")
if st.button("Fetch Weather"):
    temp_api, humidity_api = get_weather(city, api_key)
    if temp_api is not None and humidity_api is not None:
        st.success(f"Temperature: {temp_api} °C, Humidity: {humidity_api} %")
    else:
        st.error("Failed to fetch weather data for this city.")
else:
    temp_api, humidity_api = None, None

# ==== Manual Input Form with Weather API defaults ====
with st.form("manual_input"):
    st.subheader("📥 Enter Sensor Data Manually or Use Weather API")

    temp = st.number_input("🌡️ Temperature (°C)", value=temp_api if temp_api is not None else 30)
    humidity = st.number_input("💧 Humidity (%)", value=humidity_api if humidity_api is not None else 60)
    moisture = st.selectbox("🌱 Soil Moisture", ["Wet", "Dry"])
    crop = st.selectbox("🌿 Select Crop", ["Paddy", "Maize", "Wheat", "Cotton"])
    submitted = st.form_submit_button("📌 Predict")

if submitted:
    moisture_val = 0 if moisture == "Wet" else 1
    prediction = predict_irrigation(temp, humidity, moisture_val, crop)

    result_text = "✅ నీరు అవసరం లేదు" if prediction == 0 else "🚿 నీరు అవసరం ఉంది"
    st.success(result_text)

    # 🔊 Voice Output (Telugu)
    tts = gTTS(text=result_text, lang='te')
    tts.save("output.mp3")
    os.system("start output.mp3" if os.name == "nt" else "mpg321 output.mp3")

    # 🧪 Fertilizer Tip
    fert_tip = suggest_fertilizer(crop)
    st.info(f"🧪 Fertilizer Tip for {crop}: {fert_tip}")

    # 📲 Send SMS if irrigation is needed
    if prediction == 1:
        msg = (
            f"🚨 Irrigation Alert for {crop}!\n"
            f"🌡 Temperature: {temp}°C\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌱 Soil moisture: {'Dry' if moisture_val == 1 else 'Wet'}\n"
            "నీటిపోసే అవసరం ఉంది (Irrigation needed)."
        )
        send_sms_alert(msg)
        st.success("✅ SMS alert sent successfully.")

    # 💾 Save to CSV
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([[now, temp, humidity, moisture_val, crop, prediction]],
                           columns=["timestamp", "temp", "humidity", "moisture", "crop", "prediction"])
    new_row.to_csv("data/sensor_data.csv", mode='a', index=False, header=False)
    st.success("✅ Data saved successfully.")

# ==== 📊 Dashboard ====
if st.checkbox("📊 Show Dashboard"):
    try:
        df = pd.read_csv("data/sensor_data.csv", header=None)
        df.columns = ["timestamp", "temp", "humidity", "moisture", "crop", "prediction"]
        st.line_chart(df[["temp", "humidity"]])
    except:
        st.warning("⚠️ No data yet.")

# ==== 🔁 Retrain Button ====
if st.button("🔁 Retrain Model"):
    os.system("python train.py")
    st.success("✅ Model retrained successfully!")
