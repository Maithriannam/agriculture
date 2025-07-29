import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

DATA_PATH = "data/sensor_data.csv"
MODEL_PATH = "models/irrigation_model.pkl"

def train_model():
    if not os.path.exists(DATA_PATH):
        print("❌ No data to train on.")
        return

    # ✅ Load data with correct headers
    df = pd.read_csv(DATA_PATH, header=None)
    df.columns = ["timestamp", "temp", "humidity", "moisture", "crop", "prediction"]

    # ✅ Drop rows with any missing values
    df = df.dropna()

    # ✅ Remove header rows if accidentally appended
    df = df[df["temp"] != "temp"]

    # ✅ Convert necessary columns to correct types
    df["temp"] = df["temp"].astype(float)
    df["humidity"] = df["humidity"].astype(float)
    df["moisture"] = df["moisture"].astype(int)
    df["prediction"] = df["prediction"].astype(int)

    # ✅ Encode crop
    crop_encoding = {"Paddy": 0, "Maize": 1, "Wheat": 2, "Cotton": 3}
    df["crop_encoded"] = df["crop"].map(crop_encoding)

    # ✅ Drop rows with unknown crops
    df = df.dropna(subset=["crop_encoded"])

    # ✅ Features & Target
    X = df[["temp", "humidity", "moisture", "crop_encoded"]]
    y = df["prediction"]

    # ✅ Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # ✅ Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("✅ Model retrained and saved!")

if __name__ == "__main__":
    train_model()

