import streamlit as st
import pandas as pd
import datetime
import os
import requests
from gtts import gTTS
from predict import predict_irrigation
from utils.fertilizer import suggest_fertilizer
from sms_alert import send_sms_alert

st.set_page_config(page_title="🌾 Smart Agriculture", layout="centered")
st.title("🌾 Smart Agriculture Dashboard")

# ✅ Ensure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# 🌦️ Weather Fetch Function
def get_weather(city_name):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp'], data['main']['humidity']
    else:
        print("❌ Weather error:", response.text)
        return None, None

# 📤 Upload Section
st.subheader("📤 Upload Sensor Data (CSV)")
uploaded_file = st.file_uploader("Choose CSV file", type="csv")
if uploaded_file:
    df_new = pd.read_csv(uploaded_file)
    df_new.to_csv("data/sensor_data.csv", mode='a', index=False, header=False)
    st.success("✅ Data uploaded!")

# 🗑️ Delete All Data
if st.button("🗑️ Clear All Data"):
    open("data/sensor_data.csv", "w").close()
    st.success("✅ All data cleared.")

# 🌤️ Get Weather from City
st.subheader("🌤 Get Weather from City")
city = st.text_input("Enter City", "Hyderabad")
if st.button("Fetch Weather"):
    temp_api, humidity_api = get_weather(city)
    if temp_api is not None:
        st.success(f"🌡 Temp: {temp_api} °C, 💧 Humidity: {humidity_api} %")
    else:
        st.error("❌ Failed to fetch weather data.")
else:
    temp_api, humidity_api = None, None

# 📥 Manual Input Form
with st.form("input_form"):
    st.subheader("📥 Enter Sensor Data")
    temp = st.number_input("🌡️ Temperature (°C)", value=temp_api if temp_api else 30)
    humidity = st.number_input("💧 Humidity (%)", value=humidity_api if humidity_api else 60)
    moisture = st.selectbox("🌱 Soil Moisture", ["Wet", "Dry"])
    crop = st.selectbox("🌿 Select Crop", ["Paddy", "Maize", "Wheat", "Cotton"])
    submitted = st.form_submit_button("📌 Predict")

# ✅ Prediction Logic
if submitted:
    moisture_val = 0 if moisture == "Wet" else 1
    prediction = predict_irrigation(temp, humidity, moisture_val, crop)

    result_text = "✅ నీరు అవసరం లేదు" if prediction == 0 else "🚿 నీరు అవసరం ఉంది"

    # ✅ Big Bold Message with Colors
    if prediction == 0:
        st.markdown("<p style='color:green; font-size:18px; font-family:Arial;'>✅ నీరు అవసరం లేదు – భూమి తడిగా ఉంది 😊</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:green; font-size:18px; font-family:Arial;'>🚿 నీరు అవసరం ఉంది – భూమి పొడి ఉంది 💧</p>", unsafe_allow_html=True)



    # 🔊 Telugu Voice
    tts = gTTS(text=result_text, lang='te')
    tts.save("output.mp3")
    with open("output.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")
    st.success("🔊 Voice generated!")

    # 🧪 Fertilizer Suggestion
    fert_tip = suggest_fertilizer(crop)
    st.info(f"🧪 Fertilizer Tip for {crop}: {fert_tip}")

    # 📲 SMS Alert
    if prediction == 1:
        msg = (
            f"🚨 Irrigation Alert!\n🌡 Temp: {temp}°C\n💧 Humidity: {humidity}%\n"
            f"🌱 Soil: {'Dry' if moisture_val else 'Wet'}\n🌿 Crop: {crop}\n🗣 {result_text}"
        )
        send_sms_alert(msg)
        st.success("📲 SMS sent!")

    # 💾 Save to CSV
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([[now, temp, humidity, moisture_val, crop, prediction]],
                           columns=["timestamp", "temp", "humidity", "moisture", "crop", "prediction"])
    new_row.to_csv("data/sensor_data.csv", mode='a', index=False, header=False)
    st.success("✅ Data saved.")

# ✅ Optional: Show Dashboard if expert/officer
if st.checkbox("👩‍💼 Show Advanced Dashboard"):
    try:
        df = pd.read_csv("data/sensor_data.csv", header=None)
        df.columns = ["timestamp", "temp", "humidity", "moisture", "crop", "prediction"]
        st.line_chart(df[["temp", "humidity"]])
    except:
        st.warning("⚠️ No data available.")

# 🔁 Retrain Model
if st.button("🔁 Retrain Model"):
    os.system("python train.py")
    st.success("✅ Model retrained.")
