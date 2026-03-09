import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier

# ---------------- Page Config ---------------- #
st.set_page_config(layout="wide", page_title="SAR Flood Mapping with ML")

# ---------------- Sidebar ---------------- #
st.sidebar.image("MA-logo.png", use_column_width=True)
st.sidebar.markdown("## SAR-Flood-Mapping (ML Edition)")
st.sidebar.markdown(
    """
    This app predicts flood risk using a simple ML model based on user inputs.
    Replace the dummy model with your own trained model for real results.
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
    st.stop()

# ---------------- Logout ---------------- #
if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# ---------------- Main Dashboard ---------------- #
st.title("Welcome to SAR Flood Monitoring Dashboard 🌊 (ML Version)")

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

# ---------------- ML Model Training (Dummy Data) ---------------- #
# This is just for demonstration, replace with your actual model and data
def train_dummy_model():
    # Features: rainfall(mm), river_level(m), soil_moisture(%)
    X = np.array([
        [10, 2.0, 30],
        [100, 8.0, 80],
        [50, 5.0, 50],
        [200, 10.0, 90],
        [20, 3.0, 40],
        [300, 15.0, 95],
        [5, 1.5, 20],
        [400, 18.0, 98]
    ])
    # Labels: 0 = Safe, 1 = Flood Risk
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1])

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model

model = train_dummy_model()

st.markdown("### Predict Flood Risk using ML Model")

rainfall = st.number_input("Rainfall (mm)", 0, 500, 50)
river_level = st.number_input("River Level (m)", 0.0, 20.0, 5.0)
soil_moisture = st.number_input("Soil Moisture (%)", 0, 100, 40)

if st.button("Predict Flood Risk"):
    input_features = np.array([[rainfall, river_level, soil_moisture]])
    prediction = model.predict(input_features)[0]

    if prediction == 1:
        st.error("⚠️ High Flood Risk Detected! Take Precautions!")
    else:
        st.success("✅ Area is Safe. No Immediate Flood Risk.")

# ---------------- Weekly Report (Simulated) ---------------- #
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
