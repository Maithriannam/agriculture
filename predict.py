import pandas as pd
import joblib

# ✅ Load trained model
model = joblib.load("models/irrigation_model.pkl")

# ✅ Crop encoding as used during training
crop_encoding = {"Paddy": 0, "Maize": 1, "Wheat": 2, "Cotton": 3}

def predict_irrigation(temp, humidity, moisture, crop):
    # ✅ Validate crop
    if crop not in crop_encoding:
        raise ValueError(f"🚫 Unknown crop: {crop}")

    # ✅ Validate inputs
    if not (0 <= temp <= 60):
        raise ValueError("🚫 Temperature must be between 0–60°C")
    if not (0 <= humidity <= 100):
        raise ValueError("🚫 Humidity must be between 0–100%")
    if moisture not in [0, 1]:
        raise ValueError("🚫 Moisture must be 0 (Wet) or 1 (Dry)")

    # ✅ Encode crop
    crop_encoded = crop_encoding[crop]

    # ✅ Create input DataFrame
    input_df = pd.DataFrame([[temp, humidity, moisture, crop_encoded]],
                            columns=["temp", "humidity", "moisture", "crop_encoded"])

    # ✅ Predict
    prediction = model.predict(input_df)[0]
    return prediction


