import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ---------------- Page Config ---------------- #
st.set_page_config(layout="wide", page_title="SAR Flood Mapping Dashboard")

# ---------------- Sidebar ---------------- #
st.sidebar.image("MA-logo.png", use_column_width=True)
st.sidebar.markdown("## SAR-Flood-Mapping")
st.sidebar.markdown(
    """
    SAR-Flood-Mapping detects and maps flood-affected areas using Synthetic Aperture Radar (SAR) data.
    Supports disaster response, environmental monitoring, and geospatial analysis even under cloud cover.
    """
)

# ---------------- Login System ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}  # {username: password}

if not st.session_state.logged_in:
    st.subheader("Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password!")
    with col2:
        if st.button("Register"):
            if username and password:
                st.session_state.users[username] = password
                st.success("User registered! Please login now.")
            else:
                st.error("Enter both username and password.")
    st.stop()  # Stop the app until login is successful

# ---------------- Logout ---------------- #
if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# ---------------- Main Dashboard ---------------- #
st.title(f"Welcome to SAR Flood Monitoring Dashboard 🌊")

# ---------------- Karnataka Districts & Zones ---------------- #
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

st.subheader("Select Station in Karnataka")
station = st.selectbox("Station", ["Bengaluru", "Mysuru", "Mangalore", "Hubli", "Belagavi"])

st.markdown("### Current 24-Hour Flood Monitoring (District-wise)")

# Generate simulated district + zone risk levels
district_zone_risk = {}
for dist in districts:
    district_zone_risk[dist] = {zone: np.random.choice(risk_levels, p=[0.3,0.3,0.3,0.1]) for zone in zones}

# Display the table
monitoring_data = []
for dist, zones_dict in district_zone_risk.items():
    for zone, risk in zones_dict.items():
        monitoring_data.append([dist, zone, risk])

df_monitoring = pd.DataFrame(monitoring_data, columns=["District", "Zone", "Risk Level"])
st.dataframe(df_monitoring.style.applymap(
    lambda x: f'color: {status_colors[x]}' if x in status_colors else ''
))

# ---------------- Weekly Report ---------------- #
st.subheader("Weekly Flood Report")
dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
weekly_data = [np.random.randint(0, 100) for _ in range(7)]  # simulated % flood risk

df_weekly = pd.DataFrame({"Date": dates, "Flood Risk (%)": weekly_data})
df_weekly["Date"] = df_weekly["Date"].dt.strftime("%d-%b")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_weekly["Date"], df_weekly["Flood Risk (%)"], marker="o", linestyle="-", color="royalblue")
ax.set_title(f"Weekly Flood Risk Trend - Station: {station}")
ax.set_ylabel("Flood Risk (%)")
ax.set_ylim(0, 100)
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(fig)

# ---------------- Legend ---------------- #
st.markdown(
    """
    **Legend for 24-hour Monitoring Zones:**
    - 🔵 Blue → Monitoring  
    - 🔴 Red → Critical (Immediate Action)  
    - 🟢 Green → Safe  
    - 🟠 Orange → Active Alert / Requires Attention
    """
)
