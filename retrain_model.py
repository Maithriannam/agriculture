import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def retrain_model():
    df = pd.read_csv("data/sensor_data.csv", header=None)
    df.columns = ['temp', 'humidity', 'moisture']
    df['irrigation_needed'] = (df['moisture'] == 1).astype(int)
    X = df[['temp', 'humidity']]
    y = df['irrigation_needed']

    model = RandomForestClassifier()
    model.fit(X, y)
    joblib.dump(model, 'models/irrigation_model.pkl')
    return "✅ Model retrained and saved successfully!"
