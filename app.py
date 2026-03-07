"""Home page for Streamlit app."""
import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from src.config_parameters import params
from src.utils import (
    add_about,
    add_logo,
    set_home_page_style,
    toggle_menu_button,
)

# Page configuration (ONLY ONCE)
st.set_page_config(layout="wide", page_title=params["browser_title"])

# If app is deployed hide menu button
toggle_menu_button()

# Create sidebar
add_logo("MA-logo.png")
add_about()

# Set page style
set_home_page_style()

# Page title
st.markdown("# Home")

# First section
st.markdown("## Introduction")
st.markdown(
    """
    This tool allows to estimate flood extent using Sentinel-1
    synthetic-aperture radar
    <a href='%s'>SAR</a> data.<br><br>
    The methodology is based on a <a href='%s'>recommended practice</a>
    published by the United Nations Platform for Space-based Information for
    Disaster Management and Emergency Response (UN-SPIDER) and it uses several
    satellite imagery datasets to produce the final output. The datasets are
    retrieved from <a href='%s'>Google Earth Engine</a> which is a powerful
    web-platform for cloud-based processing of remote sensing data on large
    scales.
    """
    % (
        params["url_sentinel_esa"],
        params["url_unspider_tutorial"],
        params["url_gee"],
    ),
    unsafe_allow_html=True,
)

# Second section
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
This page visualizes SAR flood mapping samples using **Sentinel-1 SAR images**,
**Sentinel-2 optical images**, and **flood labels**.
"""
)

# File paths
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
