import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
import requests
import geemap
import ee

# ---------------- CONFIG ---------------- #
st.set_page_config(layout="wide", page_title="Real-Time SAR Flood Monitoring")

# ---------------- GOOGLE EARTH ENGINE ---------------- #
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("SAR Flood Monitoring (Real-Time)")

# ---------------- LOGIN SYSTEM ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {}

if not st.session_state.logged_in:

    st.title("Login / Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):

            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success("Login successful")
                st.experimental_rerun()

            else:
                st.error("Invalid login")

    with col2:
        if st.button("Register"):

            st.session_state.users[username] = password
            st.success("User Registered")

    st.stop()

# ---------------- LOGOUT ---------------- #
if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# ---------------- TITLE ---------------- #
st.title("Real-Time Flood Prediction Dashboard 🌊")

# ---------------- STATION ---------------- #
station = st.selectbox(
    "Select Station",
    ["Bengaluru", "Mysuru", "Mangalore", "Hubli", "Belagavi"]
)

# ---------------- WEATHER API ---------------- #
API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    data = response.json()

    rainfall = 0

    if "rain" in data:
        rainfall = data["rain"].get("1h", 0)

    temperature = data["main"]["temp"]

    humidity = data["main"]["humidity"]

    return rainfall, temperature, humidity

rainfall, temperature, humidity = get_weather(station)

st.subheader("Real-Time Weather Data")

col1, col2, col3 = st.columns(3)

col1.metric("Rainfall (mm)", rainfall)
col2.metric("Temperature (°C)", temperature)
col3.metric("Humidity (%)", humidity)

# ---------------- RIVER LEVEL DATA ---------------- #
river_level = st.slider("River Water Level (meters)", 0.0, 20.0, 5.0)

soil_moisture = st.slider("Soil Moisture (%)", 0, 100, 40)

# ---------------- ML MODEL ---------------- #

def train_model():

    X = np.array([
        [10,2,30],
        [100,8,80],
        [50,5,50],
        [200,10,90],
        [20,3,40],
        [300,15,95],
        [5,1,20],
        [400,18,98]
    ])

    y = np.array([0,1,0,1,0,1,0,1])

    model = RandomForestClassifier(n_estimators=100)

    model.fit(X,y)

    return model

model = train_model()

# ---------------- PREDICTION ---------------- #

st.subheader("Flood Risk Prediction")

if st.button("Predict Flood Risk"):

    features = np.array([[rainfall, river_level, soil_moisture]])

    prediction = model.predict(features)[0]

    if prediction == 1:

        st.error("⚠️ Flood Risk Detected")

    else:

        st.success("Area Safe")

# ---------------- WEEKLY TREND ---------------- #

st.subheader("Flood Risk Trend")

dates = [datetime.now() - timedelta(days=i) for i in range(6,-1,-1)]

risk = np.random.randint(0,100,7)

df = pd.DataFrame({
    "date":dates,
    "risk":risk
})

df["date"] = df["date"].dt.strftime("%d-%b")

fig, ax = plt.subplots()

ax.plot(df["date"],df["risk"],marker="o")

ax.set_ylim(0,100)

ax.set_ylabel("Flood Risk %")

ax.set_title("Weekly Flood Trend")

plt.xticks(rotation=45)

st.pyplot(fig)

# ---------------- SATELLITE FLOOD MAP ---------------- #

st.subheader("Satellite Flood Map")

Map = geemap.Map(center=[12.97,77.59], zoom=7)

dataset = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(ee.Geometry.Point([77.59,12.97])) \
            .filterDate("2024-01-01","2024-12-31")

image = dataset.first()

Map.addLayer(image, {}, "Sentinel SAR")

Map.to_streamlit(height=500)
