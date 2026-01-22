import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- FACILITY UI STYLING ---
st.set_page_config(page_title="V-MAX Assembly Guru", layout="wide", page_icon="🚀")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #f0c14b !important; font-weight: bold; }
    h1, h2, h3 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ADVANCED TRANSIENT LOGIC (SEC-TO-SEC) ---
def run_assembly_sim(temp, p_init, duration, w_cu_ratio, grain_thickness):
    t_steps = np.arange(0, duration + 1, 1)
    
    # Paraffin Regression Logic (The 'SolidWorks' Cross-Section)
    regression_rate = 0.5 # mm/s (High for Paraffin)
    remaining_fuel = grain_thickness - (regression_rate * t_steps)
    remaining_fuel = np.maximum(remaining_fuel, 0)
    
    # Performance Decay
    p_decay = p_init * (remaining_fuel / grain_thickness)**0.5
    acoustic_db = (10 * np.log10((temp/10)**4) + 120) - (0.3 * t_steps)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Fuel Web (mm)": np.round(remaining_fuel, 2),
        "Chamber Pressure (Bar)": np.round(p_decay, 2),
        "Acoustic Load (dB)": np.round(acoustic_db, 1)
    })

# --- MISSION CONTROL ---
st.title("🚀 V-MAX Master Assembly: Static Test Digital Twin")
st.markdown("#### Hardware Components: HGG Motor | Umbilical Tower | JDD Deflector")

with st.sidebar:
    st.header("Component Specs")
    t_goal = st.slider("Chamber Temp (K)", 1500, 3500, 3032) #
    p_start = st.slider("Initial Pressure (Bar)", 10, 80, 35) #
    w_cu = st.slider("W-Cu Mixer (% W)", 50, 95, 75)
    web_init = st.slider("Initial Fuel Web (mm)", 10, 50, 30)
    burn_time = st.number_input("Burn Duration (s)", 5, 60, 20)

df_sim = run_assembly_sim(t_goal, p_start, burn_time, w_cu, web_init)

# --- 3D ASSEMBLY VIEW ---
st.subheader("🔥 Live Firing & Component Interaction")
col_vis, col_data = st.columns([2, 1])

with col_vis:
    # 3D View of Cross-Sectional Firing & JDD Impingement
    x, y = np.linspace(-15, 15, 30), np.linspace(-15, 15, 30)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    # JDD Thermal Gradient Mapping [cite: 14]
    Z = (t_goal / 10) * np.exp(-0.25 * R) * (df_sim['Chamber Pressure (Bar)'].iloc[-1] / p_start)
    
    fig = go.Figure(data=[go.Surface(z=Z, colorscale='Hot', name='JDD Surface')])
    fig.update_layout(title="JDD Stagnation Point (Thermal Gradient)", 
                      template="plotly_dark", margin=dict(l=0, r=0, b=0, t=40))
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.metric("Umbilical Data", "CONNECTED")
    st.metric("Peak Acoustic Load", f"{df_sim['Acoustic Load (dB)'].max()} dB")
    st.write("Cross-Section: Fuel Regression (mm)")
    st.bar_chart(df_sim.set_index('Sec')['Fuel Web (mm)'])

st.divider()
st.info("This assembly simulates the hardware 'living' during the test. As the paraffin wax regresses, the pressure decays and the JDD heat flux updates in real-time.")
