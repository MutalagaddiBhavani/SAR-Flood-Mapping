import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="SAR Flood Monitoring Dashboard",
    layout="wide"
)

# ---------------- SESSION STATE ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {}

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- DISTRICT COORDINATES ---------------- #
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

# ---------------- WEATHER DATA ---------------- #
current_temps = {district: np.random.randint(29,38) for district in district_coords}
current_rainfall = {district: np.random.randint(0,20) for district in district_coords}

status_colors = {
    "Safe":"green",
    "Monitoring":"blue",
    "Active Alert":"orange",
    "Critical":"red"
}

# ---------------- ML TRAINING DATA ---------------- #
def generate_training_data():

    data = []

    for _ in range(500):

        rainfall = np.random.uniform(0,200)
        river = np.random.uniform(0,15)
        temp = np.random.uniform(20,40)

        if rainfall > 150 or river > 12:
            risk = "Critical"
        elif rainfall > 100 or river > 9:
            risk = "Active Alert"
        elif rainfall > 40 or river > 5:
            risk = "Monitoring"
        else:
            risk = "Safe"

        data.append([rainfall,river,temp,risk])

    df = pd.DataFrame(data,columns=["rainfall","river","temp","risk"])

    return df

df = generate_training_data()

X = df[["rainfall","river","temp"]]
y = df["risk"]

model = RandomForestClassifier()
model.fit(X,y)

# ---------------- RIVER LEVEL ---------------- #
def get_river_level():
    return round(np.random.uniform(1,15),2)

# ---------------- SIDEBAR ---------------- #
def sidebar_info():

    st.sidebar.image("images/logo.png", use_container_width=True)

    st.sidebar.markdown("## SAR Flood Mapping")

    st.sidebar.markdown(
        """
SAR-Flood-Mapping detects flood-affected regions using Synthetic Aperture Radar (SAR)
satellite imagery and machine learning.

It helps disaster management authorities monitor flood risk even during
cloud cover or night conditions.
"""
    )

# ---------------- LOGIN PAGE ---------------- #
def login_page():

    sidebar_info()

    st.title("SAR Flood Monitoring Dashboard - Login/Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1,col2 = st.columns(2)

    with col1:

        if st.button("Login"):

            if username in st.session_state.users and st.session_state.users[username] == password:

                st.session_state.logged_in = True
                st.session_state.page = "monitoring"

            else:

                st.error("User not registered")

    with col2:

        if st.button("Register"):

            if username and password:

                st.session_state.users[username] = password
                st.success("User Registered")

# ---------------- LOGOUT ---------------- #
def logout():

    st.session_state.logged_in = False
    st.session_state.page = "login"

# ---------------- MONITORING PAGE ---------------- #
def monitoring_page():

    sidebar_info()

    st.title("24-Hour Flood Monitoring")

    st.button("Logout", on_click=logout)

    district = st.selectbox("Select District", list(district_coords.keys()))

    lat,lon = district_coords[district]

    temp = current_temps[district]
    rainfall = current_rainfall[district]
    river = get_river_level()

    col1,col2,col3 = st.columns(3)

    col1.metric("Temperature °C", temp)
    col2.metric("Rainfall mm", rainfall)
    col3.metric("River Level m", river)

    # ML Prediction
    prediction = model.predict([[rainfall,river,temp]])

    risk = prediction[0]

    st.markdown(
        f"### Flood Risk Status: <span style='color:{status_colors[risk]}'>{risk}</span>",
        unsafe_allow_html=True
    )

    # Map
    st.markdown("### District Location")

    m = folium.Map(location=[lat,lon], zoom_start=9)

    folium.Marker(
        [lat,lon],
        popup=f"{district} - {risk}",
        tooltip=district,
        icon=folium.Icon(color=status_colors[risk])
    ).add_to(m)

    st_folium(m,width=700,height=400)

    if st.button("Weekly Report"):

        st.session_state.page = "weekly_report"

# ---------------- WEEKLY REPORT ---------------- #
def weekly_report():

    sidebar_info()

    st.title("Weekly Flood Trend")

    st.button("Back", on_click=lambda: st.session_state.update({"page":"monitoring"}))

    district = st.selectbox("District", list(district_coords.keys()))

    base_rain = current_rainfall[district]

    dates = [datetime.now() - timedelta(days=i) for i in range(6,-1,-1)]

    flood_risk = [min(100,max(0, base_rain*0.6 + np.random.uniform(0,15))) for _ in range(7)]

    df = pd.DataFrame({
        "Date":dates,
        "Flood Risk":flood_risk
    })

    df["Date"] = df["Date"].dt.strftime("%d-%b")

    fig,ax = plt.subplots()

    ax.plot(df["Date"],df["Flood Risk"],marker="o")

    ax.set_ylim(0,100)

    ax.set_title(f"Weekly Flood Trend - {district}")

    plt.grid(True)

    st.pyplot(fig)

# ---------------- MAIN ---------------- #
if not st.session_state.logged_in:

    login_page()

elif st.session_state.page == "monitoring":

    monitoring_page()

elif st.session_state.page == "weekly_report":

    weekly_report()
