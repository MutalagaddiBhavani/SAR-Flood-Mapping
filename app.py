import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import os
import folium
import json
from streamlit_folium import st_folium

# ---------------- Page Config ---------------- #
st.set_page_config(layout="wide", page_title="SAR Flood Monitoring Dashboard")

# ---------------- Session State ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "page" not in st.session_state:
    st.session_state.page = "login"  # login, dashboard, mapping

# ---------------- Login/Register Page ---------------- #
def login_page():
    st.title("Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.page = "dashboard"
                st.success(f"Welcome {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password!")
    with col2:
        if st.button("Register"):
            if username and password:
                st.session_state.users[username] = password
                st.success("User registered! Please login now.")
            else:
                st.error("Enter both username and password.")

# ---------------- Logout Button ---------------- #
def logout():
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.experimental_rerun()

# ---------------- Karnataka Districts ---------------- #
district_coords = {
    "Bengaluru Urban": (12.9716, 77.5946),
    "Bengaluru Rural": (13.1976, 77.7066),
    "Mysuru": (12.2958, 76.6394),
    "Mangalore": (12.9141, 74.8560),
    "Hubli-Dharwad": (15.3647, 75.1232),
    "Belagavi": (15.8497, 74.4977),
    "Ballari": (15.1394, 76.9214),
    "Chikkamagaluru": (13.3151, 75.7750),
    "Davanagere": (14.4647, 75.9210),
    "Tumakuru": (13.3409, 77.1010),
    "Shimoga": (13.9299, 75.5681),
    "Raichur": (16.2076, 77.3463),
    "Kalaburagi": (17.3297, 76.8343),
    "Bidar": (17.9133, 77.5280),
    "Udupi": (13.3409, 74.7421),
    "Hassan": (13.0072, 76.1025),
    "Mandya": (12.5240, 76.8970),
    "Kodagu": (12.3375, 75.8069),
    "Chitradurga": (14.2319, 76.4026),
    "Kolar": (13.1366, 78.1296),
    "Chamarajanagar": (11.9184, 77.0200),
    "Ramanagara": (12.7237, 77.2810),
    "Haveri": (14.8000, 75.4000),
    "Gadag": (15.4319, 75.6350),
    "Yadgir": (16.7695, 77.1375),
    "Bagalkot": (16.1660, 75.6769),
    "Vijayapura": (16.8300, 75.7100),
    "Bagepalli": (13.3039, 78.0803),
    "Koppal": (15.3453, 76.1548),
    "Chikkaballapur": (13.4360, 77.7276)
}

zones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
risk_levels = ["Safe", "Monitoring", "Active Alert", "Critical"]
status_colors = {"Safe": "green", "Monitoring": "blue", "Active Alert": "orange", "Critical": "red"}

# ---------------- Dashboard Page ---------------- #
def dashboard_page():
    st.title("SAR Flood Monitoring Dashboard 🌊")
    st.button("Logout", on_click=logout)

    st.subheader("Select District")
    district = st.selectbox("District", list(district_coords.keys()))
    
    # 24-hour district risk monitoring (simulated)
    st.markdown("### 24-Hour Flood Monitoring (District-wise)")
    district_zone_risk = {}
    for dist in district_coords.keys():
        district_zone_risk[dist] = {zone: np.random.choice(risk_levels, p=[0.3,0.3,0.3,0.1]) for zone in zones}

    monitoring_data = []
    for dist, zones_dict in district_zone_risk.items():
        for zone, risk in zones_dict.items():
            monitoring_data.append([dist, zone, risk])

    df_monitoring = pd.DataFrame(monitoring_data, columns=["District", "Zone", "Risk Level"])
    st.dataframe(df_monitoring.style.applymap(lambda x: f'color: {status_colors[x]}' if x in status_colors else ''))

    st.subheader("Weekly Flood Report")
    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    weekly_data = [np.random.randint(0, 100) for _ in range(7)]
    df_weekly = pd.DataFrame({"Date": dates, "Flood Risk (%)": weekly_data})
    df_weekly["Date"] = df_weekly["Date"].dt.strftime("%d-%b")

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df_weekly["Date"], df_weekly["Flood Risk (%)"], marker="o", linestyle="-", color="royalblue")
    ax.set_title(f"Weekly Flood Risk Trend - District: {district}")
    ax.set_ylabel("Flood Risk (%)")
    ax.set_ylim(0,100)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

    if st.button("Go to Flood Mapping Page"):
        st.session_state.page = "mapping"
        st.experimental_rerun()

# ---------------- Flood Mapping Page ---------------- #
def mapping_page():
    st.title("Flood Mapping & SAR Images 🛰️")
    st.button("Back to Dashboard", on_click=lambda: st.session_state.update({"page":"dashboard"}))
    
    st.subheader("Select District")
    district = st.selectbox("District", list(district_coords.keys()))
    lat, lon = district_coords[district]

    # Real-time weather
    def get_weather(lat, lon):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            r = requests.get(url, timeout=5)
            data = r.json()
            weather = data.get('current_weather', {})
            rainfall = weather.get('precipitation', 0)
            wind = weather.get('windspeed', 0)
            temp = weather.get('temperature', 0)
        except:
            rainfall = wind = temp = 0
        return rainfall, wind, temp

    rainfall, wind, temp = get_weather(lat, lon)
    st.metric("Rainfall (mm)", rainfall)
    st.metric("Wind Speed (km/h)", wind)
    st.metric("Temperature (°C)", temp)

    # SAR Image display
    st.subheader("Latest SAR Image")
    sar_folder = "S1"
    sar_image_file = os.path.join(sar_folder, f"{district.replace(' ','_')}_SAR.png")
    if os.path.exists(sar_image_file):
        st.image(sar_image_file, caption=f"{district} SAR Image", use_column_width=True)
        st.markdown(f"[Open in new tab]({sar_image_file})", unsafe_allow_html=True)
    else:
        st.info("SAR Image not available for this district yet.")

    # Map visualization
    st.subheader("District Map")
    m = folium.Map(location=[lat, lon], zoom_start=7)
    folium.Marker([lat, lon], tooltip=district, popup=f"{district} Rainfall: {rainfall}mm").add_to(m)
    geojson_file = "Sen1Floods11_Metadata.geojson"
    if os.path.exists(geojson_file):
        with open(geojson_file) as f:
            geojson_data = json.load(f)
        folium.GeoJson(geojson_data, name="Districts").add_to(m)
    st_folium(m, width=700, height=500)

# ---------------- Page Control ---------------- #
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
elif st.session_state.page == "mapping":
    mapping_page()
