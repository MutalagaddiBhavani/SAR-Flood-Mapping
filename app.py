import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import requests

# -------- Page Config -------- #
st.set_page_config(layout="wide", page_title="SAR Flood Monitoring")

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
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # <-- Yahan apni API key dalen

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&units=metric&appid={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].title()
            return temp, desc
        else:
            return None, None
    except Exception:
        return None, None

# -------- Login/Register Page -------- #
def login_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)  # Sidebar logo
    st.title("Login / Register")
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
                    st.error("Incorrect password! ❌")
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
                st.error("Enter both username and password!")

# -------- Logout -------- #
def logout():
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.experimental_rerun()

# -------- District-wise 24-Hour Flood Monitoring Page -------- #
def monitoring_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)  # Sidebar logo
    st.title("24-Hour Flood Monitoring (District-wise)")
    st.button("Logout", on_click=logout)

    district_selected = st.selectbox("Select District", districts)

    # Fetch weather for the selected district (city name approximate)
    # Note: Some district names might differ from city names recognized by OpenWeatherMap
    city_for_weather = district_selected.split()[0]  # Take first word for simplicity
    temp, desc = get_weather(city_for_weather)

    if temp is not None:
        st.markdown(f"### Current Temperature in {district_selected}: {temp} °C")
        st.markdown(f"**Weather:** {desc}")
    else:
        st.markdown(f"Weather data not available for {district_selected}.")

    # Simulated district + zone risk levels
    district_zone_risk = {}
    for dist in districts:
        district_zone_risk[dist] = {zone: np.random.choice(risk_levels, p=[0.3,0.3,0.3,0.1]) for zone in zones}

    monitoring_data = []
    for dist, zones_dict in district_zone_risk.items():
        for zone, risk in zones_dict.items():
            monitoring_data.append([dist, zone, risk])

    df_monitoring = pd.DataFrame(monitoring_data, columns=["District", "Zone", "Risk Level"])
    df_filtered = df_monitoring[df_monitoring["District"] == district_selected]

    def color_risk(val):
        return f'color: {status_colors.get(val, "black")}'
    st.dataframe(df_filtered.style.applymap(color_risk, subset=["Risk Level"]), height=400)

    if st.button("Go to Weekly Report"):
        st.session_state.page = "weekly_report"
        st.experimental_rerun()

# -------- Weekly Report Page -------- #
def weekly_report_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)  # Sidebar logo
    st.title("Weekly Flood Risk Report")
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
