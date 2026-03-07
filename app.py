"""Full SAR Flood Mapping + India Flood Monitoring Dashboard"""
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

# ---------------- PAGE CONFIGURATION ---------------- #
st.set_page_config(layout="wide", page_title=params["browser_title"])

# Hide menu button if deployed
toggle_menu_button()

# Create sidebar
add_logo("MA-logo.png")
add_about()

# Set page style
set_home_page_style()

# ---------------- HOME SECTION ---------------- #
st.markdown("# Home")

st.markdown("## Introduction")
st.markdown(
    """
    This tool allows estimating flood extent using Sentinel-1
    synthetic-aperture radar (<a href='%s'>SAR</a>) data.<br><br>
    The methodology is based on a <a href='%s'>recommended practice</a>
    by the UN-SPIDER and uses several satellite datasets processed on
    <a href='%s'>Google Earth Engine</a>.
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
        <li>Use the drawing tool to select an area of interest.</li>
        <li>Choose image dates before and after the flood event.</li>
        <li>Adjust parameters like threshold and pass direction.</li>
        <li>Click <i>Compute flood extent</i> to generate the flood map.</li>
        <li>Export the raster/vector flood layer if needed.</li>
    </ul>
    """,
    unsafe_allow_html=True,
)

# ---------------- FLOOD VISUALIZATION SECTION ---------------- #
st.markdown("---")
st.title("🌊 SAR Flood Mapping Visualization")

st.markdown(
    """
Visualizes SAR flood mapping samples using **Sentinel-1 SAR images**, 
**Sentinel-2 optical images**, and **flood labels**.
"""
)

# File paths (sample data)
S1_PATH = "Sample/S1/Spain_7370579_S1Hand.tif"
S2_PATH = "Sample/S2/Spain_7370579_S2Hand.tif"
LABEL_PATH = "Sample/Labels/Spain_7370579_LabelHand.tif"

# Function to read raster
def load_raster(path):
    with rasterio.open(path) as src:
        img = src.read(1)
    return img

# Load images
try:
    s1 = load_raster(S1_PATH)
    s2 = load_raster(S2_PATH)
    label = load_raster(LABEL_PATH)
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# Plot images
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
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

# ---------------- INDIA FLOOD MONITORING DASHBOARD ---------------- #
st.markdown("---")
st.title("🌏 India Flood Monitoring Dashboard")

st.markdown(
"""
Color-coded states and cities indicate flood risk:
- 🔵 Blue → Monitoring
- 🔴 Red → Critical (Immediate Action)
- 🟢 Green → Safe
- 🟠 Orange → Active Alert / Requires Attention
"""
)

# Example state/city data
flood_data = {
    "West Bengal": {"risk": "Critical", "cities": ["Kolkata", "Siliguri", "Asansol"]},
    "Odisha": {"risk": "Active Alert", "cities": ["Bhubaneswar", "Cuttack", "Puri"]},
    "Bihar": {"risk": "Monitoring", "cities": ["Patna", "Gaya", "Muzaffarpur"]},
    "Kerala": {"risk": "Safe", "cities": ["Thiruvananthapuram", "Kochi", "Kozhikode"]},
    "Assam": {"risk": "Critical", "cities": ["Guwahati", "Dibrugarh", "Silchar"]},
    "Tamil Nadu": {"risk": "Active Alert", "cities": ["Chennai", "Coimbatore", "Madurai"]}
}

# Risk color mapping
risk_colors = {"Monitoring": "blue", "Critical": "red", "Safe": "green", "Active Alert": "orange"}

# Interactive map
m = folium.Map(location=[22.0, 80.0], zoom_start=5)
city_coords_example = {
    "Kolkata": [22.5726, 88.3639], "Siliguri": [26.7271, 88.3953], "Asansol": [23.6850, 86.9524],
    "Bhubaneswar": [20.2961, 85.8245], "Cuttack": [20.4625, 85.8828], "Puri": [19.8135, 85.8312],
    "Patna": [25.5941, 85.1376], "Gaya": [24.7956, 85.0], "Muzaffarpur": [26.1209, 85.3647],
    "Thiruvananthapuram": [8.5241, 76.9366], "Kochi": [9.9312, 76.2673], "Kozhikode": [11.2588, 75.7804],
    "Guwahati": [26.1445, 91.7362], "Dibrugarh": [27.4728, 94.9110], "Silchar": [24.8330, 92.7780],
    "Chennai": [13.0827, 80.2707], "Coimbatore": [11.0168, 76.9558], "Madurai": [9.9252, 78.1198]
}

for state, info in flood_data.items():
    color = risk_colors[info["risk"]]
    for city in info["cities"]:
        coords = city_coords_example.get(city, [22.0, 80.0])
        folium.CircleMarker(
            location=coords,
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            popup=f"{city}, {state} ({info['risk']})"
        ).add_to(m)

st_folium(m, width=700, height=500)

# ---------------- CITY COUNT SUMMARY ---------------- #
st.markdown("---")
st.subheader("City Count by Risk Level")
summary = {key: 0 for key in risk_colors.keys()}
for info in flood_data.values():
    summary[info["risk"]] += len(info["cities"])
for risk, count in summary.items():
    st.markdown(f"**{risk}**: {count} cities")

# ---------------- DETAILED STATE/CITY LIST ---------------- #
st.markdown("---")
st.subheader("States and Cities with Risk Levels")
for state, info in flood_data.items():
    st.markdown(f"**{state}** ({info['risk']}): {', '.join(info['cities'])}")

# ---------------- EMERGENCY ALERTS ---------------- #
st.markdown("---")
st.subheader("🚨 Emergency Alerts")
for state, info in flood_data.items():
    if info["risk"] == "Critical":
        st.error(f"{state} is in CRITICAL flood condition! Immediate action required in cities: {', '.join(info['cities'])}")
