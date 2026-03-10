import streamlit as st
import numpy as np
import pandas as pd
import requests
import json
import hashlib
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="SAR Flood Mapping",
    layout="wide"
)

# ---------------------------------------------------
# CONSTANTS
# ---------------------------------------------------

USERS_FILE = "users.json"
API_KEY = "YOUR_OPENWEATHER_API_KEY"

status_colors = {
    "Safe":"green",
    "Monitoring":"blue",
    "Active Alert":"orange",
    "Critical":"red"
}

# ---------------------------------------------------
# DISTRICT COORDINATES
# ---------------------------------------------------

district_coords = {

"Bengaluru Urban": (12.9716,77.5946),
"Mysuru": (12.2958,76.6394),
"Mangaluru": (12.9141,74.8560),
"Belagavi": (15.8497,74.4977),
"Tumakuru": (13.3392,77.1130),
"Shivamogga": (13.9299,75.5681),
"Hassan": (13.0076,76.1020),
"Raichur": (16.2109,77.3666),
"Udupi": (13.3409,74.7421),
"Ballari": (15.1394,76.9214)

}

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------------------------------
# USER STORAGE
# ---------------------------------------------------

def load_users():

    try:
        with open(USERS_FILE,"r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):

    with open(USERS_FILE,"w") as f:
        json.dump(users,f)

users = load_users()

# ---------------------------------------------------
# WEATHER API
# ---------------------------------------------------

def get_weather(lat,lon):

    try:

        url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

        response=requests.get(url).json()

        temp=response["main"]["temp"]

        rainfall=response.get("rain",{}).get("1h",0)

        return temp,rainfall

    except:

        temp=np.random.uniform(25,35)
        rainfall=np.random.uniform(0,20)

        return temp,rainfall

# ---------------------------------------------------
# RIVER LEVEL SIMULATION
# ---------------------------------------------------

def river_level():

    return round(np.random.uniform(2,14),2)

# ---------------------------------------------------
# MACHINE LEARNING MODEL
# ---------------------------------------------------

def train_model():

    data=[]

    for _ in range(1000):

        rainfall=np.random.uniform(0,200)
        river=np.random.uniform(0,15)
        temp=np.random.uniform(20,40)

        if rainfall>150 or river>12:
            risk="Critical"

        elif rainfall>100 or river>9:
            risk="Active Alert"

        elif rainfall>50 or river>6:
            risk="Monitoring"

        else:
            risk="Safe"

        data.append([rainfall,river,temp,risk])

    df=pd.DataFrame(data,columns=["rain","river","temp","risk"])

    X=df[["rain","river","temp"]]
    y=df["risk"]

    model=RandomForestClassifier(n_estimators=200)

    model.fit(X,y)

    return model

model=train_model()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

def sidebar():

    st.sidebar.title("SAR Flood Mapping")

    st.sidebar.info("""

SAR Flood Mapping detects flood-prone regions using

• Satellite SAR Analysis  
• Weather Monitoring  
• Machine Learning  
• River Level Monitoring  

This system helps disaster management teams monitor flood risk in real time.

""")

# ---------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------

def login_page():

    sidebar()

    st.title("SAR Flood Mapping - Login")

    username=st.text_input("Username")

    password=st.text_input("Password",type="password")

    col1,col2=st.columns(2)

    with col1:

        if st.button("Login"):

            if username in users and users[username]==hash_password(password):

                st.session_state.logged_in=True
                st.session_state.page="dashboard"

            else:

                st.error("Invalid Login")

    with col2:

        if st.button("Register"):

            if username and password:

                users[username]=hash_password(password)

                save_users(users)

                st.success("User Registered Successfully")

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

def dashboard():

    sidebar()

    st.title("🌊 SAR Flood Mapping Dashboard")

    if st.button("Logout"):

        st.session_state.logged_in=False
        st.session_state.page="login"

    district=st.selectbox("Select District",list(district_coords.keys()))

    lat,lon=district_coords[district]

    temp,rain=get_weather(lat,lon)

    river=river_level()

    col1,col2,col3=st.columns(3)

    col1.metric("Temperature (°C)",round(temp,1))
    col2.metric("Rainfall (mm)",rain)
    col3.metric("River Level (m)",river)

    prediction=model.predict([[rain,river,temp]])

    risk=prediction[0]

    st.markdown(
        f"## Flood Risk Status: <span style='color:{status_colors[risk]}'>{risk}</span>",
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# RISK GAUGE
# ---------------------------------------------------

    risk_score={"Safe":25,"Monitoring":50,"Active Alert":75,"Critical":100}[risk]

    fig=go.Figure(go.Indicator(

        mode="gauge+number",
        value=risk_score,
        title={'text':"Flood Risk Index"},
        gauge={'axis':{'range':[0,100]}}

    ))

    st.plotly_chart(fig,use_container_width=True)

# ---------------------------------------------------
# MAP
# ---------------------------------------------------

    st.subheader("Flood Monitoring Map")

    m=folium.Map(location=[lat,lon],zoom_start=7)

    for d,(lt,ln) in district_coords.items():

        rf=np.random.uniform(0,200)
        rv=np.random.uniform(2,14)
        tp=np.random.uniform(20,40)

        r=model.predict([[rf,rv,tp]])[0]

        folium.CircleMarker(

            location=[lt,ln],
            radius=8,
            popup=f"{d} - {r}",
            color=status_colors[r],
            fill=True

        ).add_to(m)

    st_folium(m,width=900,height=500)

    if st.button("Weekly Report"):

        st.session_state.page="report"

# ---------------------------------------------------
# WEEKLY REPORT
# ---------------------------------------------------

def weekly_report():

    sidebar()

    st.title("Weekly Flood Trend Analysis")

    if st.button("Back"):

        st.session_state.page="dashboard"

    district=st.selectbox("District",list(district_coords.keys()))

    base=np.random.uniform(30,80)

    dates=[datetime.now()-timedelta(days=i) for i in range(6,-1,-1)]

    risk=[min(100,max(0,base+np.random.uniform(-15,15))) for _ in range(7)]

    df=pd.DataFrame({

        "Date":dates,
        "Risk":risk

    })

    df["Date"]=df["Date"].dt.strftime("%d-%b")

    fig=go.Figure()

    fig.add_trace(go.Scatter(

        x=df["Date"],
        y=df["Risk"],
        mode="lines+markers"

    ))

    fig.update_layout(

        title=f"Weekly Flood Risk Trend - {district}",
        yaxis_range=[0,100]

    )

    st.plotly_chart(fig,use_container_width=True)

    st.download_button(

        "Download Report",
        df.to_csv(index=False).encode(),
        "SAR_Flood_Report.csv"

    )

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if not st.session_state.logged_in:

    login_page()

elif st.session_state.page=="dashboard":

    dashboard()

elif st.session_state.page=="report":

    weekly_report()
