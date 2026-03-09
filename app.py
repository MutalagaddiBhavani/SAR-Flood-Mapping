import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# ---------------- Page Config ---------------- #
st.set_page_config(layout="wide", page_title="SAR Flood Monitoring Dashboard")

# ---------------- Session State ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- Districts & Coordinates ---------------- #
district_coords = {
    "Bagalkot": (16.1667, 75.7000),
    "Ballari": (15.1394, 76.9214),
    "Belagavi": (15.8497, 74.4977),
    "Bengaluru Rural": (12.9770, 77.5660),
    "Bengaluru Urban": (12.9716, 77.5946),
    "Bidar": (17.9133, 77.5299),
    "Chamarajanagar": (11.9141, 76.9507),
    "Chikkaballapura": (13.4357, 77.7299),
    "Chikkamagaluru": (13.3193, 75.7754),
    "Chitradurga": (14.2300, 76.4000),
    "Dakshina Kannada": (12.9141, 74.8560),
    "Davanagere": (14.4667, 75.9167),
    "Dharwad": (15.4589, 75.0078),
    "Gadag": (15.4270, 75.6320),
    "Hassan": (13.0076, 76.1020),
    "Haveri": (14.8000, 75.4000),
    "Kalaburagi": (17.3297, 76.8343),
    "Kodagu": (12.3375, 75.8069),
    "Kolar": (13.1363, 78.1298),
    "Koppal": (15.3456, 76.1545),
    "Mandya": (12.5231, 76.8950),
    "Mysuru": (12.2958, 76.6394),
    "Raichur": (16.2109, 77.3666),
    "Ramanagara": (12.7024, 77.2852),
    "Shivamogga": (13.9299, 75.5681),
    "Tumakuru": (13.3392, 77.1130),
    "Udupi": (13.3409, 74.7421),
    "Uttara Kannada": (14.6166, 74.6165),
    "Vijayapura": (16.8302, 75.7100),
    "Yadgir": (16.7742, 77.1322)
}

# ---------------- Actual Temperatures (°C) ---------------- #
current_temps = {
    "Bagalkot": 37, "Ballari": 36, "Belagavi": 34, "Bengaluru Rural": 33,
    "Bengaluru Urban": 33, "Bidar": 35, "Chamarajanagar": 32, "Chikkaballapura": 33,
    "Chikkamagaluru": 30, "Chitradurga": 35, "Dakshina Kannada": 31, "Davanagere": 36,
    "Dharwad": 35, "Gadag": 35, "Hassan": 31, "Haveri": 35, "Kalaburagi": 36,
    "Kodagu": 29, "Kolar": 33, "Koppal": 36, "Mandya": 33, "Mysuru": 32,
    "Raichur": 37, "Ramanagara": 33, "Shivamogga": 33, "Tumakuru": 34,
    "Udupi": 31, "Uttara Kannada": 31, "Vijayapura": 36, "Yadgir": 36
}

# ---------------- Approximate Rainfall (mm) ---------------- #
current_rainfall = {
    "Bagalkot": 2, "Ballari": 0, "Belagavi": 10, "Bengaluru Rural": 5,
    "Bengaluru Urban": 6, "Bidar": 1, "Chamarajanagar": 7, "Chikkaballapura": 4,
    "Chikkamagaluru": 12, "Chitradurga": 3, "Dakshina Kannada": 15, "Davanagere": 2,
    "Dharwad": 1, "Gadag": 1, "Hassan": 8, "Haveri": 1, "Kalaburagi": 0,
    "Kodagu": 18, "Kolar": 5, "Koppal": 0, "Mandya": 7, "Mysuru": 6,
    "Raichur": 0, "Ramanagara": 5, "Shivamogga": 12, "Tumakuru": 4,
    "Udupi": 15, "Uttara Kannada": 14, "Vijayapura": 0, "Yadgir": 0
}

risk_levels = ["Safe","Monitoring","Active Alert","Critical"]
status_colors = {"Safe":"green","Monitoring":"blue","Active Alert":"orange","Critical":"red"}

# ---------------- Dummy River Data ---------------- #
def get_dummy_river_level(lat, lon):
    return round(np.random.uniform(1,15),2)

# ---------------- Sidebar Info ---------------- #
def sidebar_info():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.sidebar.markdown("## SAR Flood Mapping")
    st.sidebar.markdown(
        "SAR-Flood-Mapping is a project for detecting and mapping flood-affected areas "
        "using Synthetic Aperture Radar (SAR) satellite imagery. It processes SAR data "
        "to identify water bodies and generate flood extent maps, supporting disaster "
        "response, environmental monitoring, and geospatial analysis even under cloud "
        "cover or low-light conditions."
    )

# ---------------- Login Page ---------------- #
def login_page():
    sidebar_info()
    st.title("SAR Flood Monitoring Dashboard - Login/Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username]==password:
                st.session_state.logged_in=True
                st.session_state.page="monitoring"
            else:
                st.error("User not registered. Please register first!")
    with col2:
        if st.button("Register"):
            if username and password:
                st.session_state.users[username]=password
                st.success("User registered! Please login now.")
            else:
                st.error("Enter both username and password.")

def logout():
    st.session_state.logged_in=False
    st.session_state.page="login"

# ---------------- Monitoring Page ---------------- #
def monitoring_page():
    sidebar_info()
    st.title("24-Hour Flood Monitoring (District-wise)")
    st.button("Logout", on_click=logout)
    
    district = st.selectbox("Select District", list(district_coords.keys()))
    lat, lon = district_coords[district]
    
    temp = current_temps.get(district,33)
    rainfall = current_rainfall.get(district,5)
    river_level = get_dummy_river_level(lat, lon)
    
    st.metric("Temperature (°C)", temp)
    st.metric("Rainfall (mm)", rainfall)
    st.metric("River Level (m)", river_level)
    
    risk_score = rainfall*0.6 + river_level*0.4
    risk = "Critical" if risk_score>50 else "Active Alert" if risk_score>30 else "Monitoring" if risk_score>10 else "Safe"
    st.markdown(f"**Flood Risk Status:** <span style='color:{status_colors[risk]}'>{risk}</span>", unsafe_allow_html=True)
    
    st.markdown("### District Location")
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup=f"{district} - {risk}", tooltip=district,
                  icon=folium.Icon(color=status_colors[risk])).add_to(m)
    st_folium(m, width=700, height=400)
    
    if st.button("Weekly Report"):
        st.session_state.page="weekly_report"

# ---------------- Weekly Report ---------------- #
def weekly_report():
    sidebar_info()
    st.title("Weekly Flood Report")
    st.button("Back", on_click=lambda: st.session_state.update({"page":"monitoring"}))
    
    district = st.selectbox("Select District for Weekly Trend", list(district_coords.keys()))
    temp = current_temps.get(district,33)
    base_rain = current_rainfall.get(district,5)
    
    # Precompute 7-day flood risk trend based on rainfall + random variation
    dates = [datetime.now()-timedelta(days=i) for i in range(6,-1,-1)]
    flood_risk = [min(100, max(0, base_rain*0.6 + np.random.uniform(0,15))) for _ in range(7)]
    
    df = pd.DataFrame({"Date": dates, "Flood Risk (%)": flood_risk})
    df["Date"] = df["Date"].dt.strftime("%d-%b")
    
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df["Date"], df["Flood Risk (%)"], marker="o", linestyle="-", color="royalblue")
    ax.set_ylim(0,100)
    ax.set_ylabel("Flood Risk (%)")
    ax.set_title(f"Weekly Flood Risk Trend - {district}")
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

# ---------------- Main ---------------- #
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page=="monitoring":
    monitoring_page()
elif st.session_state.page=="weekly_report":
    weekly_report()
