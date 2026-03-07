"""SAR Flood Monitoring App - Karnataka"""
import streamlit as st
import rasterio
import matplotlib.pyplot as plt
import numpy as np

# ----------------- APP CONFIG ----------------- #
st.set_page_config(page_title="SAR Flood Monitoring - Karnataka", layout="wide")

# ----------------- SESSION STATE ----------------- #
if "users" not in st.session_state:
    st.session_state.users = {}  # dynamic username:password
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------- HOME PAGE ----------------- #
st.title("🏠 Karnataka SAR Flood Monitoring Tool")

st.markdown("""
## Introduction
This tool estimates flood extent using **Sentinel-1 SAR data**.

The methodology is based on a UN-SPIDER recommended practice and uses satellite datasets processed on **Google Earth Engine**.
""")

st.markdown("""
## How to use the tool
1. Signup/Login as a rescuer.
2. Select a Station to see districts under it.
3. View SAR flood samples.
4. Monitor 24-hour and weekly flood chances.
""")

st.markdown("---")

# ----------------- LOGIN / SIGNUP ----------------- #
st.header("🔑 Rescuer Access")
tab1, tab2 = st.tabs(["Login", "Signup"])

with tab1:
    st.subheader("Login")
    login_user = st.text_input("Username", key="login_user")
    login_pass = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if login_user in st.session_state.users and st.session_state.users[login_user] == login_pass:
            st.session_state.logged_in = True
            st.session_state.username = login_user
            st.success(f"Welcome back, {login_user}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

with tab2:
    st.subheader("Signup")
    signup_user = st.text_input("Choose Username", key="signup_user")
    signup_pass = st.text_input("Choose Password", type="password", key="signup_pass")
    if st.button("Signup"):
        if signup_user in st.session_state.users:
            st.error("Username already exists")
        elif signup_user == "" or signup_pass == "":
            st.warning("Enter both username and password")
        else:
            st.session_state.users[signup_user] = signup_pass
            st.success(f"Account created for {signup_user}! Please login now.")

# ----------------- MAIN DASHBOARD ----------------- #
if st.session_state.logged_in:
    st.markdown("---")
    st.header(f"🏡 Welcome {st.session_state.username} - Karnataka Dashboard")

    # ----------------- STATIONS & DISTRICTS ----------------- #
    st.subheader("📍 Karnataka Stations")
    stations = {
        "Station North": ["Bangalore Rural", "Chikmagalur", "Belgaum"],
        "Station East": ["Kolar", "Chikkaballapur", "Tumkur"],
        "Station South": ["Mysore", "Chamarajanagar", "Mandya"],
        "Station West": ["Udupi", "Dakshina Kannada", "Karwar"]
    }

    selected_station = st.selectbox("Select a Station", list(stations.keys()))
    st.markdown(f"### Districts under **{selected_station}**")
    st.write(", ".join(stations[selected_station]))

    # ----------------- SAMPLE SAR VISUALIZATION ----------------- #
    st.subheader("🌊 SAR Flood Mapping Sample")
    S1_PATH = "Sample/S1/Spain_7370579_S1Hand.tif"
    S2_PATH = "Sample/S2/Spain_7370579_S2Hand.tif"
    LABEL_PATH = "Sample/Labels/Spain_7370579_LabelHand.tif"

    def load_raster(path):
        try:
            with rasterio.open(path) as src:
                return src.read(1)
        except:
            return None

    s1 = load_raster(S1_PATH)
    s2 = load_raster(S2_PATH)
    label = load_raster(LABEL_PATH)

    if s1 is not None and s2 is not None and label is not None:
        fig, ax = plt.subplots(1, 3, figsize=(18, 6))
        ax[0].imshow(s1, cmap="gray"); ax[0].set_title("Sentinel-1 SAR")
        ax[1].imshow(s2, cmap="terrain"); ax[1].set_title("Sentinel-2 Optical")
        ax[2].imshow(label, cmap="Blues"); ax[2].set_title("Flood Label")
        for a in ax: a.axis("off")
        st.pyplot(fig)
    else:
        st.warning("SAR sample files not found. Skipping visualization.")

    # ----------------- WEEKLY FLOOD REPORT ----------------- #
    st.subheader("📊 Weekly Flood Chance Report")
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    weekly_chance = np.random.randint(20, 80, size=7)  # Simulated data
    fig2, ax2 = plt.subplots()
    ax2.plot(days, weekly_chance, marker="o", color="blue")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Flood Chance (%)")
    ax2.set_title("Karnataka Weekly Flood Monitoring")
    st.pyplot(fig2)

    # ----------------- 24-HOUR MONITORING ----------------- #
    st.subheader("⏱️ 24-Hour Flood Monitoring")
    hours = [f"{h}:00" for h in range(24)]
    hourly_chance = np.random.randint(10, 70, size=24)
    fig3, ax3 = plt.subplots(figsize=(12,4))
    ax3.plot(hours, hourly_chance, marker="o", color="orange")
    ax3.set_ylim(0, 100)
    ax3.set_ylabel("Flood Chance (%)")
    ax3.set_title("24-Hour Flood Monitoring")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # ----------------- LOGOUT ----------------- #
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()
