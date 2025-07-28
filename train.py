import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Make sure models folder exists
os.makedirs("models", exist_ok=True)

# Load sensor data with header
df = pd.read_csv("data/sensor_data.csv")

# If your CSV doesn't have headers, specify them here:
# df = pd.read_csv("data/sensor_data.csv", names=["timestamp", "temp", "humidity", "moisture", "crop", "prediction"])

# Check dataframe columns
print(df.columns)

# Crop encoding - convert crop names to numeric labels
df['crop_encoded'] = df['crop'].astype('category').cat.codes

# Define features and target
X = df[['temp', 'humidity', 'moisture', 'crop_encoded']]
y = df['prediction']

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "models/irrigation_model.pkl")

print("✅ Model trained and saved.")


