"""Full SAR Flood Mapping + All-India Flood Monitoring Dashboard with Zones"""
import streamlit as st
import rasterio
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from src.config_parameters import params
from src.utils import (
    add_about,
    add_logo,
    set_home_page_style,
    toggle_menu_button,
)

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(layout="wide", page_title=params["browser_title"])
toggle_menu_button()
add_logo("MA-logo.png")
add_about()
set_home_page_style()

# ---------------- HOME SECTION ---------------- #
st.markdown("# Home")

st.markdown("## Introduction")
st.markdown(
    """
This tool estimates flood extent using Sentinel-1 synthetic-aperture radar
(<a href='%s'>SAR</a>) data processed via <a href='%s'>UN-SPIDER recommended
practice</a> on <a href='%s'>Google Earth Engine</a>.
"""
    % (
        params["url_sentinel_esa"],
        params["url_unspider_tutorial"],
        params["url_gee"],
    ),
    unsafe_allow_html=True,
)

st.markdown("## How to use the tool")
st.markdown(
    """
<ul>
<li>Select <i>Flood extent analysis</i> in the sidebar.</li>
<li>Draw an area of interest on the map.</li>
<li>Choose analysis dates before/after flood period.</li>
<li>Adjust threshold and pass direction.</li>
<li>Click <i>Compute flood extent</i> to generate flood mapping.</li>
<li>Export results if needed.</li>
</ul>
""",
    unsafe_allow_html=True,
)

# ---------------- SAR VISUALIZATION ---------------- #
st.markdown("---")
st.title("🌊 SAR Flood Mapping Visualization")

st.markdown(
    """
This section visualizes Sentinel-1 SAR, Sentinel-2 optical, and flood label samples.
"""
)

S1_PATH = "Sample/S1/Spain_7370579_S1Hand.tif"
S2_PATH = "Sample/S2/Spain_7370579_S2Hand.tif"
LABEL_PATH = "Sample/Labels/Spain_7370579_LabelHand.tif"

def load_raster(path):
    with rasterio.open(path) as src:
        return src.read(1)

try:
    s1 = load_raster(S1_PATH)
    s2 = load_raster(S2_PATH)
    label = load_raster(LABEL_PATH)
except Exception as e:
    st.error(f"Error loading raster samples: {e}")
    st.stop()

fig, ax = plt.subplots(1, 3, figsize=(18, 5))
ax[0].imshow(s1, cmap="gray")
ax[0].set_title("Sentinel-1 SAR")
ax[1].imshow(s2, cmap="terrain")
ax[1].set_title("Sentinel-2 Optical")
ax[2].imshow(label, cmap="Blues")
ax[2].set_title("Flood Label")
for a in ax:
    a.axis("off")
st.pyplot(fig)
st.success("Flood sample visualization loaded.")

# ---------------- INDIA FLOOD MONITORING ZONES ---------------- #
st.markdown("---")
st.title("🌏 India Flood Monitoring Dashboard - Zonal View")

st.markdown(
    """
Flood risk zones in all 8 directions are color-coded:
🔵 Blue → Monitoring  
🔴 Red → Critical (Immediate Action)  
🟢 Green → Safe  
🟠 Orange → Active Alert / Requires Attention
"""
)

# Define zones for each state/UT
directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# Example random flood risk assignment per zone (update with real data)
import random
risk_levels = ["Monitoring", "Critical", "Safe", "Active Alert"]
risk_colors = {"Monitoring": "blue", "Critical": "red", "Safe": "green", "Active Alert": "orange"}

# List of Indian States + UTs
states_uts = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman & Nicobar", "Chandigarh", "Dadra & Nagar Haveli", "Daman & Diu",
    "Delhi", "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

# Assign zones
state_zones = {}
for state in states_uts:
    state_zones[state] = {dir: random.choice(risk_levels) for dir in directions}

# Build folium map
india_map = folium.Map(location=[22, 80], zoom_start=5)

# Approximate center coordinates for each state (can refine)
state_coords = {
    "Andhra Pradesh": [15.9129, 79.74],
    "Arunachal Pradesh": [28.2180, 94.7278],
    "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131],
    "Chhattisgarh": [21.2787, 81.8661],
    "Goa": [15.2993, 74.1240],
    "Gujarat": [22.2587, 71.1924],
    "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [31.1048, 77.1734],
    "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [15.3173, 75.7139],
    "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [23.4733, 77.9470],
    "Maharashtra": [19.7515, 75.7139],
    "Manipur": [24.6637, 93.9063],
    "Meghalaya": [25.4670, 91.3662],
    "Mizoram": [23.1645, 92.9376],
    "Nagaland": [26.1584, 94.5624],
    "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412],
    "Rajasthan": [27.0238, 74.2179],
    "Sikkim": [27.5330, 88.5122],
    "Tamil Nadu": [11.1271, 78.6569],
    "Telangana": [18.1124, 79.0193],
    "Tripura": [23.9408, 91.9882],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550],
    "Andaman & Nicobar": [11.7401, 92.6586],
    "Chandigarh": [30.7333, 76.7794],
    "Dadra & Nagar Haveli": [20.1809, 73.0169],
    "Daman & Diu": [20.4283, 72.8397],
    "Delhi": [28.6139, 77.2090],
    "Jammu & Kashmir": [33.7782, 76.5762],
    "Ladakh": [34.1526, 77.5770],
    "Lakshadweep": [10.5667, 72.6417],
    "Puducherry": [11.9416, 79.8083]
}

# Plot each zone per state as colored marker (simplified)
for state, zones in state_zones.items():
    lat, lon = state_coords.get(state, [22, 80])
    # For each direction, create a small circle offset to represent the zone
    offset_map = {
        "N": (0.3, 0), "NE": (0.2, 0.2), "E": (0, 0.3), "SE": (-0.2, 0.2),
        "S": (-0.3, 0), "SW": (-0.2, -0.2), "W": (0, -0.3), "NW": (0.2, -0.2)
    }
    for dir, risk in zones.items():
        off_lat, off_lon = offset_map[dir]
        folium.CircleMarker(
            location=[lat + off_lat, lon + off_lon],
            radius=5,
            color=risk_colors[risk],
            fill=True,
            fill_color=risk_colors[risk],
            popup=f"{state} - {dir} zone ({risk})"
        ).add_to(india_map)

# Display map
try:
    st_folium(india_map, width=800, height=500, key="india_flood_zones")
except Exception as e:
    st.error(f"Map rendering error: {e}")

# ---------------- SUMMARY ---------------- #
st.markdown("---")
st.subheader("📊 Flood Zone Count by Risk Level")
summary = {risk: 0 for risk in risk_levels}
for zones in state_zones.values():
    for risk in zones.values():
        summary[risk] += 1
for risk, count in summary.items():
    st.markdown(f"**{risk}**: {count} zones")

# ---------------- LIST STATES & ZONES ---------------- #
st.markdown("---")
st.subheader("🗺️ States & Zone-wise Risk Levels")
for state, zones in state_zones.items():
    zone_info = ", ".join([f"{dir}:{risk}" for dir, risk in zones.items()])
    st.markdown(f"**{state}** → {zone_info}")

# ---------------- EMERGENCY ALERTS ---------------- #
st.markdown("---")
st.subheader("🚨 Emergency Alerts")
for state, zones in state_zones.items():
    critical_zones = [dir for dir, risk in zones.items() if risk == "Critical"]
    if critical_zones:
        st.error(f"{state} has CRITICAL zones in directions: {', '.join(critical_zones)}. Immediate action required!")
