import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import requests
from twilio.rest import Client

# -------- Page Config -------- #
st.set_page_config(layout="wide", page_title="SAR Flood Monitoring Dashboard")

# -------- Session State -------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------- Constants -------- #
districts = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mangalore", "Hubli-Dharwad",
    "Belagavi", "Ballari", "Chikkamagaluru", "Davanagere", "Tumakuru",
    "Shimoga", "Raichur", "Kalaburagi", "Bidar", "Udupi", "Hassan",
    "Mandya", "Kodagu", "Chitradurga", "Kolar", "Chamarajanagar",
    "Ramanagara", "Haveri", "Gadag", "Yadgir", "Bagalkot", "Vijayapura",
    "Bagepalli", "Koppal", "Chikkaballapur"
]
zones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
risk_levels = ["Safe", "Monitoring", "Active Alert", "Critical"]
status_colors = {
    "Safe": "green",
    "Monitoring": "blue",
    "Active Alert": "orange",
    "Critical": "red"
}

# -------- OpenWeatherMap API key -------- #
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # put your API key here

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&units=metric&appid={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].title()
            rain_1h = data.get("rain", {}).get("1h", 0)
            return temp, desc, rain_1h
        else:
            return None, None, None
    except Exception:
        return None, None, None

# -------- Twilio SMS Example -------- #
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_FROM = "+1234567890"  # Twilio number

def send_sms(message, to_number):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(body=message, from_=TWILIO_FROM, to=to_number)

# -------- Login/Register Page -------- #
def login_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("SAR Flood Monitoring Dashboard - Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if username in st.session_state.users:
                if st.session_state.users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.page = "monitoring"
                    st.success(f"Welcome {username}!")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect password!")
            else:
                st.warning("User not registered! Please register first.")

    with col2:
        if st.button("Register"):
            if username and password:
                if username not in st.session_state.users:
                    st.session_state.users[username] = password
                    st.success("User registered successfully! ✅ Please login.")
                else:
                    st.info("User already exists. Please login.")
            else:
                st.error("Please enter both Username and Password!")

# -------- Logout -------- #
def logout():
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.experimental_rerun()

# -------- Monitoring Page -------- #
def monitoring_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("24-Hour Flood Monitoring (District-wise) - SAR")
    st.button("Logout", on_click=logout)

    district_selected = st.selectbox("Select District", districts)
    city_for_weather = district_selected.split()[0]
    temp, desc, rainfall = get_weather(city_for_weather)

    if temp is not None:
        st.markdown(f"### 🌡️ Temperature: {temp} °C")
        st.markdown(f"Weather: {desc}")
        st.markdown(f"🌧️ Rainfall last 1h: {rainfall} mm")
    else:
        st.markdown("Weather data not available.")

    # Dummy river water level
    river_level = np.random.uniform(2.0, 8.0)
    st.markdown(f"🌊 River Water Level: {river_level:.2f} m")

    # Simulated 24-hour flood risk
    district_zone_risk = {dist: {zone: np.random.choice(risk_levels, p=[0.3,0.3,0.3,0.1]) for zone in zones} for dist in districts}
    monitoring_data = []
    for dist, zones_dict in district_zone_risk.items():
        for zone, risk in zones_dict.items():
            monitoring_data.append([dist, zone, risk])

    df_monitoring = pd.DataFrame(monitoring_data, columns=["District", "Zone", "Risk Level"])
    df_filtered = df_monitoring[df_monitoring["District"] == district_selected]
    st.dataframe(df_filtered.style.applymap(lambda x: f'color: {status_colors.get(x,"black")}', subset=["Risk Level"]), height=400)

    # Dummy AI Flood Detection Map
    st.markdown("### 🛰️ AI Flood Detection Map (Dummy Example)")
    flood_map = np.random.randint(0,2,(100,100))
    plt.imshow(flood_map, cmap="Blues")
    plt.title(f"{district_selected} Flood Map")
    st.pyplot(plt.gcf())
    
    if st.button("Go to Weekly Report"):
        st.session_state.page = "weekly_report"
        st.experimental_rerun()

# -------- Weekly Report -------- #
def weekly_report_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("Weekly Flood Report - SAR")
    st.button("Back to Monitoring", on_click=lambda: change_page("monitoring"))
    st.button("Logout", on_click=logout)

    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    weekly_data = [np.random.randint(0, 100) for _ in range(7)]
    df_weekly = pd.DataFrame({"Date": dates, "Flood Risk (%)": weekly_data})
    df_weekly["Date"] = df_weekly["Date"].dt.strftime("%d-%b")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_weekly["Date"], df_weekly["Flood Risk (%)"], marker="o", linestyle="-", color="royalblue")
    ax.set_title("Weekly Flood Risk Trend")
    ax.set_ylabel("Flood Risk (%)")
    ax.set_ylim(0, 100)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

def change_page(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# -------- Main -------- #
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page == "monitoring":
    monitoring_page()
elif st.session_state.page == "weekly_report":
    weekly_report_page()
