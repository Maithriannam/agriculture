import streamlit as st
import pandas as pd
import datetime
import os
import requests
import base64
import tempfile
from gtts import gTTS
from predict import predict_irrigation
from utils.fertilizer import suggest_fertilizer
from sms_alert import send_sms_alert
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()


st.set_page_config(page_title="🌾 SMART AGRICULTURE", layout="centered")

# Title + Header
st.title("🌾 Smart Agriculture Dashboard")
st.markdown("Welcome to the **Smart Agriculture App**. Make informed decisions on irrigation and fertilizers using live weather and soil moisture data.")

# Create data directory
if not os.path.exists("data"):
    os.makedirs("data")

# ⛅ Cached Weather Fetcher
@st.cache_data(ttl=1800)
def get_weather(city_name):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        res = requests.get(url, params={"q": city_name, "appid": api_key, "units": "metric"})
        data = res.json()
        if res.status_code == 200:
            return data["main"]["temp"], data["main"]["humidity"]
    except:
        return None, None
    return None, None

# 🔊 Voice Playback
@st.cache_data
def generate_voice(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        gTTS(text=text, lang='te').save(tmpfile.name)
        with open(tmpfile.name, "rb") as audio_file:
            b64 = base64.b64encode(audio_file.read()).decode()
    return b64

def play_voice(text):
    try:
        b64 = generate_voice(text)
        st.markdown(
            f"""<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>""",
            unsafe_allow_html=True
        )
        st.success("🔊 Voice Note Sent!")
    except Exception as e:
        st.error(f"❌ Voice Failed: {e}")

# ⚙️ Sidebar Settings
st.sidebar.title("⚙️ Settings")
auto_predict = st.sidebar.toggle("🔁 Auto Predict Every 30 Min", value=True)
enable_voice = st.sidebar.toggle("🔊 Voice Alerts", value=True)
enable_sms = st.sidebar.toggle("📲 SMS Alerts", value=True)
allow_repeat = st.sidebar.toggle("🔁 Allow Repeat Alerts", value=True)

# 🧠 Session State
if 'last_alert' not in st.session_state:
    st.session_state.last_alert = None


st.subheader("🌦️ Weather-Based Prediction")
city = st.text_input("📍 Enter City", "Hyderabad")
crop = st.selectbox("🌾 Crop", ["Paddy", "Maize", "Wheat", "Cotton"])
moisture = st.selectbox("🌱 Soil Moisture", ["Wet", "Dry"])
moisture_val = 0 if moisture == "Wet" else 1

if auto_predict and city:
    temp, humidity = get_weather(city)
    if temp is not None and humidity is not None:
        prediction = predict_irrigation(temp, humidity, moisture_val, crop)
        result_text = "✅ నీరు అవసరం లేదు" if prediction == 0 else "🚿 నీరు పోసే అవసరం ఉంది"

        st.markdown(f"<p style='font-size:18px; color:green;'>🗣️ {result_text}</p>", unsafe_allow_html=True)

        
        if enable_voice:
            play_voice(result_text)

        
        st.markdown("### 🧪 Fertilizer Recommendation")
        fert_tip = suggest_fertilizer(crop)
        st.info(f"{fert_tip}")

    
        if enable_sms and (allow_repeat or st.session_state.last_alert != prediction):
            msg = (
                f"🚨 Irrigation Alert!\n🌡 Temp: {temp}°C\n💧 Humidity: {humidity}%\n"
                f"🌱 Moisture: {'Dry' if moisture_val else 'Wet'}\n🌿 Crop: {crop}\n🗣 {result_text}"
            )
            status = send_sms_alert(msg)
            if status and "limit" in status.lower():
                st.error("❌ SMS Limit Reached")
            elif status:
                st.success("📲 SMS Sent Successfully")
            else:
                st.error("❌ SMS Failed to Send")

    
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = pd.DataFrame([[now, temp, humidity, moisture_val, crop, prediction]],
                           columns=["timestamp", "temp", "humidity", "moisture", "crop", "prediction"])
        row.to_csv("data/sensor_data.csv", mode='a', index=False, header=False)
        st.session_state.last_alert = prediction

    
        st.success("🎉 All steps completed: Prediction ✔️ | Voice ✔️ | Fertilizer ✔️ | SMS ✔️")
        st.balloons()
    else:
        st.error("❌ Could not fetch weather. Check API key or city name.")
with st.form("manual_form"):
    st.subheader("✍️ Manual Prediction")
    temp_manual = st.number_input("🌡️ Temperature", value=30)
    humidity_manual = st.number_input("💧 Humidity", value=60)
    moisture_manual = st.selectbox("🌱 Moisture", ["Wet", "Dry"], key="manual_m")
    crop_manual = st.selectbox("🌾 Crop", ["Paddy", "Maize", "Wheat", "Cotton"], key="manual_c")
    submit = st.form_submit_button("📌 Predict")

if submit:
    moisture_val_manual = 0 if moisture_manual == "Wet" else 1
    prediction = predict_irrigation(temp_manual, humidity_manual, moisture_val_manual, crop_manual)
    result_text = "✅ నీరు అవసరం లేదు" if prediction == 0 else "🚿 నీరు పోసే అవసరం ఉంది"
    st.success(result_text)

    if enable_voice:
        play_voice(result_text)

    st.info(f"🧪 Fertilizer Suggestion: {suggest_fertilizer(crop_manual)}")

    if enable_sms and prediction == 1:
        status = send_sms_alert(f"Manual Alert: {result_text} for {crop_manual}")
        if status and "limit" in status.lower():
            st.error("❌ SMS Limit Reached")
        elif status:
            st.success("📲 Manual SMS Sent!")
        else:
            st.error("❌ SMS Failed")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = pd.DataFrame([[now, temp_manual, humidity_manual, moisture_val_manual, crop_manual, prediction]],
                       columns=["timestamp", "temp", "humidity", "moisture", "crop", "prediction"])
    row.to_csv("data/sensor_data.csv", mode='a', index=False, header=False)

# 📤 Upload CSV
st.subheader("📤 Upload CSV")
upload = st.file_uploader("Upload CSV File", type="csv")
if upload:
    pd.read_csv(upload).to_csv("data/sensor_data.csv", mode='a', index=False, header=False)
    st.success("✅ CSV Uploaded!")

# 🗑️ Clear All Data
if st.button(" Clear All Data"):
    open("data/sensor_data.csv", "w").close()
    st.success("✅ Data Cleared!")

# 📊 Dashboard
if st.checkbox("📊 Show Dashboard"):
    try:
        df = pd.read_csv("data/sensor_data.csv", header=None)
        df.columns = ["timestamp", "temp", "humidity", "moisture", "crop", "prediction"]
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.markdown("### 📋 Recent Predictions Table")
        st.dataframe(df.tail(10))

        st.markdown("### 📈 Sensor Data Over Time")
        st.markdown("🕒 **X-axis** = Time | 🌡️ **Y-axis** = Temperature / Humidity")
        st.markdown("📌 Each dot shows one prediction record over time.")
        chart_df = df[["timestamp", "temp", "humidity"]].tail(10)
        chart_df.set_index("timestamp", inplace=True)
        st.line_chart(chart_df)
    except:
        st.warning("⚠️ No data or CSV error!")

# 🔁 Retrain Model
if st.button("🔁 Retrain Model"):
    with st.spinner("⏳ Training model..."):
        os.system("python train.py")

