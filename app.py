import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import os

# ---------------- Page Config ---------------- #
st.set_page_config(layout="wide", page_title="SAR Flood Monitoring Dashboard")

# ---------------- Session State ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- Districts ---------------- #
district_coords = {
    "Bengaluru Urban": (12.9716, 77.5946),
    "Mysuru": (12.2958, 76.6394),
    "Mangalore": (12.9141, 74.8560),
    "Hubli-Dharwad": (15.3647, 75.1240),
    "Belagavi": (15.8497, 74.4977)
    # add other districts similarly
}

zones = ["N","NE","E","SE","S","SW","W","NW"]
risk_levels = ["Safe","Monitoring","Active Alert","Critical"]
status_colors = {"Safe":"green","Monitoring":"blue","Active Alert":"orange","Critical":"red"}

# ---------------- Dummy Weather & River Data ---------------- #
def get_dummy_weather(lat, lon):
    temp = np.random.randint(18,32)
    rainfall = np.random.randint(0,100)
    return temp, rainfall

def get_dummy_river_level(lat, lon):
    level = np.random.uniform(1,15)
    return round(level,2)

# ---------------- Login Page ---------------- #
def login_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("SAR Flood Monitoring Dashboard - Login/Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.page = "monitoring"
            else:
                st.error("User not registered. Please register first!")
    
    with col2:
        if st.button("Register"):
            if username and password:
                st.session_state.users[username] = password
                st.success("User registered! Please login now.")
            else:
                st.error("Enter both username and password.")

def logout():
    st.session_state.logged_in = False
    st.session_state.page = "login"

# ---------------- Monitoring Page ---------------- #
def monitoring_page():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("24-Hour Flood Monitoring (District-wise)")
    st.button("Logout", on_click=logout)
    
    district = st.selectbox("Select District", list(district_coords.keys()))
    lat, lon = district_coords[district]
    
    # Dummy weather & river data
    temp, rainfall = get_dummy_weather(lat, lon)
    river_level = get_dummy_river_level(lat, lon)
    
    st.metric("Temperature (°C)", temp)
    st.metric("Rainfall (mm)", rainfall)
    st.metric("River Level (m)", river_level)
    
    # Flood risk calculation
    risk_score = rainfall*0.6 + river_level*0.4
    risk = "Critical" if risk_score>50 else "Active Alert" if risk_score>30 else "Monitoring" if risk_score>10 else "Safe"
    st.markdown(f"**Flood Risk Status:** <span style='color:{status_colors[risk]}'>{risk}</span>", unsafe_allow_html=True)
    
    # SAR Image display (dummy)
    sar_img_path = f"SAR_Images/{district.replace(' ','_')}.png"
    if os.path.exists(sar_img_path):
        st.image(sar_img_path, caption=f"{district} SAR Image", use_column_width=True)
    else:
        st.warning("SAR Image not available for this district yet.")
    
    # Flood heatmap (dummy)
    st.markdown("### Flood Heatmap")
    heat = np.random.randint(0,100,(10,10))
    plt.imshow(heat, cmap="hot")
    plt.colorbar(label="Flood Probability")
    st.pyplot(plt.gcf())
    
    if st.button("Weekly Report"):
        st.session_state.page = "weekly_report"

# ---------------- Weekly Report ---------------- #
def weekly_report():
    st.sidebar.image("MA-logo.png", use_column_width=True)
    st.title("Weekly Flood Report")
    st.button("Back", on_click=lambda: st.session_state.update({"page":"monitoring"}))
    
    dates = [datetime.now() - timedelta(days=i) for i in range(6,-1,-1)]
    flood_risk = np.random.randint(0,100,7)
    
    df = pd.DataFrame({"Date": dates, "Flood Risk (%)": flood_risk})
    df["Date"] = df["Date"].dt.strftime("%d-%b")
    
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df["Date"], df["Flood Risk (%)"], marker="o", linestyle="-", color="royalblue")
    ax.set_ylim(0,100)
    ax.set_ylabel("Flood Risk (%)")
    ax.set_title("Weekly Flood Risk Trend")
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(fig)

# ---------------- Main ---------------- #
if not st.session_state.logged_in:
    login_page()
elif st.session_state.page == "monitoring":
    monitoring_page()
elif st.session_state.page == "weekly_report":
    weekly_report()
