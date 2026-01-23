import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | 1.55kN Master", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE THRUST-ANCHORED PHYSICS ENGINE ---
def run_vmax_final_master(target_f_n, duration, water_lpm, theta, throat_init_mm):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Back-calculate Chamber Pressure (Pc) for 1.55kN
    # F = Cf * Pc * At (Cf ~1.45 for Methane-Oxygen expansion)
    at_initial = (np.pi * (throat_init_mm/1000)**2) / 4
    cf = 1.45 
    p_req_pa = target_f_n / (cf * at_initial)
    p_req_bar = p_req_pa / 1e5
    
    # 2. Iterative Erosion & Thrust Decay Loop
    erosion_list, p_list, thrust_list = [], [], []
    current_dia = throat_init_mm
    
    for t in t_steps:
        # As throat area (At) grows, Pressure drops (Pc ~ 1/At)
        area_ratio = (throat_init_mm**2) / (current_dia**2)
        p_inst = p_req_bar * area_ratio
        
        # Scouring Rate Logic for W-Cu Mixer
        rate = (3000/3032) * (p_inst/35) * 0.022
        current_dia += (2 * rate)
        
        erosion_list.append((current_dia - throat_init_mm) / 2)
        p_list.append(p_inst)
        thrust_list.append(target_f_n * area_ratio)

    # 3. JDD Sustainability (Transpiration Logic)
    # Factorizing Heat Flux based on Thrust-Impact
    theta_rad = np.radians(theta)
    req_lpm_list = [((p * (3000/1050) * np.sin(theta_rad)) / 1.08) * 0.4 * 60 for p in p_list]
    
    # 4. Acoustic Load (Lighthill's Law)
    # Exit Velocity (Ve) derived from Thrust & Mass Flow
    ve = 2850 # m/s (Propulsion constant for 3000K mixture)
    acoustic_db = 120 + 10 * np.log10(np.clip((ve**8) / 1e12, 1.0, 1e20))

    return pd.DataFrame({
        "Sec": t_steps,
        "Thrust (N)": np.round(thrust_list, 1),
        "Erosion (mm)": np.round(erosion_list, 3),
        "Pressure (Bar)": np.round(p_list, 2),
        "Req. Water (LPM)": np.round(req_lpm_list, 1)
    }), p_req_bar, acoustic_db

# --- DASHBOARD INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: 1.55 kN Mission Master")
st.markdown("**Status:** Requirement-Driven Model Active | **Anchor:** Target Thrust")

# Sidebar for Setup
with st.sidebar:
    st.header("🎯 Mission Parameters")
    target_f = st.number_input("Target Thrust (N)", value=1550)
    throat_mm = st.number_input("Initial Throat (mm)", value=21.04)
    st.header("🌊 Facility Limits")
    actual_water = st.number_input("Current Water Flow (LPM)", value=424)
    jdd_angle = st.slider("JDD Angle (°)", 5, 90, 45)
    burn_time = st.number_input("Burn Duration (s)", value=20)

# Run Calculations
df, p_start, db_level = run_vmax_final_master(target_f, burn_time, actual_water, jdd_angle, throat_mm)

# --- RESULTS SUMMARY ---

r1, r2, r3, r4 = st.columns(4)
r1.metric("Required Pc", f"{p_start:.2f} Bar")
r2.metric("Final Thrust", f"{df['Thrust (N)'].iloc[-1]} N")
r3.metric("Max Erosion", f"{df['Erosion (mm)'].iloc[-1]} mm")
r4.metric("Acoustic Load", f"{db_level:.0f} dB")

# --- VISUAL ANALYTICS ---

st.subheader("📊 Performance & Sustainability Curves")
a1, a2 = st.columns(2)
with a1:
    fig_f = go.Figure(go.Scatter(x=df['Sec'], y=df['Thrust (N)'], line=dict(color='gold', width=3)))
    fig_f.update_layout(title="Predicted Thrust Decay", template="plotly_dark", xaxis_title="Seconds", yaxis_title="Newtons")
    st.plotly_chart(fig_f, use_container_width=True)

with a2:
    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(x=df['Sec'], y=df['Req. Water (LPM)'], name="Required", line=dict(color='cyan')))
    fig_w.add_hline(y=actual_water, line_dash="dash", line_color="red", annotation_text="Facility Limit (424 LPM)")
    fig_w.update_layout(title="Water Sustainability Analysis", template="plotly_dark", xaxis_title="Seconds", yaxis_title="LPM")
    st.plotly_chart(fig_w, use_container_width=True)

# Safety Warning Logic

if df['Req. Water (LPM)'].max() > actual_water:
    st.error(f"⚠️ SAFETY ALERT: 1.55 kN plume at {jdd_angle}° exceeds facility cooling. Reduce angle to ~11° or upgrade pump.")
else:
    st.success(f"✅ MISSION SAFE: 424 LPM is sufficient for current configuration.")

st.dataframe(df, use_container_width=True)
