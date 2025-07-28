import pandas as pd
import joblib

model = joblib.load("models/irrigation_model.pkl")
crop_encoding = {"Paddy": 0, "Maize": 1, "Wheat": 2, "Cotton": 3}

def predict_irrigation(temp, humidity, moisture, crop):
    if crop not in crop_encoding:
        raise ValueError(f"Unknown crop: {crop}")
    if not (0 <= temp <= 60):
        raise ValueError("Temp must be 0-60 °C")
    if not (0 <= humidity <= 100):
        raise ValueError("Humidity must be 0-100%")
    if moisture not in [0,1]:
        raise ValueError("Moisture must be 0 or 1")
    crop_encoded = crop_encoding[crop]
    input_df = pd.DataFrame([[temp, humidity, moisture, crop_encoded]],
                            columns=["temp", "humidity", "moisture", "crop_encoded"])
    return model.predict(input_df)[0]
