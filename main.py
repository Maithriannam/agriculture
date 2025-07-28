import subprocess
import os

subprocess.Popen(["python3", "raspberry/sensor_reader.py"])
os.system("streamlit run app.py")
