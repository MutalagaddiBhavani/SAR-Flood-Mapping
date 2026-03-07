# app.py
import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import pandas as pd
import random

from src.config_parameters import params
from src.utils import add_about, add_logo, set_home_page_style, toggle_menu_button

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(layout="wide", page_title=params["browser_title"])
toggle_menu_button()
add_logo("MA-logo.png")
add_about()
set_home_page_style()

# ---------------- HOME PAGE ---------------- #
st.markdown("# Home")
st.markdown("## Introduction")
st.markdown(f"""
This tool estimates flood extent using **Sentinel-1 SAR data**.<br><br>
Methodology: <a href='{params['url_unspider_tutorial']}'>UN-SPIDER Guide</a> | 
<a href='{params['url_gee']}'>Google Earth Engine</a>
""", unsafe_allow_html=True)

st.markdown("## How to use the tool")
st.markdown("""
1. Check flood risk per **station zone**.  
2. Each rescuer accesses their **assigned station/zone**.  
3. Station color indicates flood risk: 🔵 Monitoring, 🟢 Safe, 🟠 Active Alert, 🔴 Critical.  
4. 24-hour and weekly trends help plan rescues.
""", unsafe_allow_html=True)

# ---------------- FLOOD VISUALIZATION ---------------- #
st.markdown("---")
st.title("🌊 SAR Flood Mapping Visualization")

# Sample file paths
S1_PATH = "Sample/S1/Spain_7370579_S1Hand.tif"
S2_PATH = "Sample/S2/Spain_7370579_S2Hand.tif"
LABEL_PATH = "Sample/Labels/Spain_7370579_LabelHand.tif"

def load_raster(path):
    with rasterio.open(path) as src:
        img = src.read(1)
    return img

try:
    s1 = load_raster(S1_PATH)
    s2 = load_raster(S2_PATH)
    label = load_raster(LABEL_PATH)
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

fig, ax = plt.subplots(1, 3, figsize=(18,6))
ax[0].imshow(s1, cmap="gray")
ax[0].set_title("Sentinel-1 SAR Image")
ax[1].imshow(s2, cmap="terrain")
ax[1].set_title("Sentinel-2 Optical Image")
ax[2].imshow(label, cmap="Blues")
ax[2].set_title("Flood Label")
for a in ax:
    a.axis("off")
st.pyplot(fig)
st.success("Flood sample loaded successfully.")

# ---------------- STATIONS & ZONES ---------------- #
st.markdown("---")
st.title("🌏 Station Zone Monitoring")

directions = ["N","NE","E","SE","S","SW","W","NW"]
risk_levels = ["Monitoring", "Safe", "Active Alert", "Critical"]
color_map = {"Monitoring":"blue", "Safe":"green", "Active Alert":"orange", "Critical":"red"}

# Create stations for 8 directions
stations = {}
base_lat, base_lon = 20.5, 78.5  # example central point
for i, dir in enumerate(directions):
    stations[f"Station {dir}"] = {
        "lat": base_lat + 0.1*(i%3),
        "lon": base_lon + 0.1*(i//3),
        "zone": dir,
        "risk": random.choices(risk_levels, weights=[0.3,0.3,0.2,0.2], k=1)[0]
    }

# ---------------- RESCUER LOGIN ---------------- #
st.markdown("## Rescuer Access")
station_names = list(stations.keys())
assigned_station = st.selectbox("Select your station:", station_names)
station_data = stations[assigned_station]

st.markdown(f"**Assigned Zone:** {station_data['zone']}")
st.markdown(f"**Current Flood Risk:** {station_data['risk']} : {color_map[station_data['risk']].upper()}")

if station_data["risk"] in ["Critical","Active Alert"]:
    st.warning(f"🚨 Immediate action required for {assigned_station}!")

# ---------------- STATION MAP ---------------- #
m = folium.Map(location=[station_data["lat"], station_data["lon"]], zoom_start=7)
for name, data in stations.items():
    folium.Marker(
        location=[data["lat"], data["lon"]],
        popup=f"{name} | Zone: {data['zone']} | Risk: {data['risk']}",
        icon=folium.Icon(color=color_map[data["risk"]], icon="tint", prefix='fa')
    ).add_to(m)
st_folium(m, width=700, height=500)

# ---------------- 24-HOUR MONITORING ---------------- #
st.markdown("---")
st.markdown("## ⏱ 24-Hour Monitoring for Your Zone")
hours = list(range(24))
zone_monitor = [random.choice(risk_levels) for _ in hours]
df_24h = pd.DataFrame({assigned_station: zone_monitor}, index=[f"{h}:00" for h in hours])
st.dataframe(df_24h)

fig, ax = plt.subplots(figsize=(10,5))
for r in risk_levels:
    ax.plot(hours, [1 if zone_monitor[h]==r else 0 for h in hours], label=r, marker='o')
ax.set_xticks(hours)
ax.set_xlabel("Hour")
ax.set_ylabel("Risk Flag")
ax.set_title(f"24-Hour Flood Risk Monitoring for {assigned_station}")
ax.legend()
st.pyplot(fig)

# ---------------- WEEKLY REPORT ---------------- #
st.markdown("---")
st.markdown("## 📊 Weekly Report for Your Zone")
days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
weekly_monitor = [random.choice(risk_levels) for _ in days]
df_week = pd.DataFrame({assigned_station: weekly_monitor}, index=days)
st.dataframe(df_week)

fig, ax = plt.subplots(figsize=(10,5))
for r in risk_levels:
    ax.plot(days, [1 if weekly_monitor[i]==r else 0 for i in range(7)], label=r, marker='o')
ax.set_xlabel("Day")
ax.set_ylabel("Risk Flag")
ax.set_title(f"Weekly Flood Risk Summary for {assigned_station}")
ax.legend()
st.pyplot(fig)

st.success("Station-wise monitoring and weekly report displayed successfully.")
