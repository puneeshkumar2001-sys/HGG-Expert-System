import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io

# --- WORLD-CLASS UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Final Aerospace Deployment", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE SUPREME PHYSICS ENGINE ---
# Grounded in Isentropic Flow Theory and Heat Balance Equations
def run_vmax_final_twin(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching (Real-Gas Correction)
    # Targets gamma approx 1.21 for methane-oxygen expansion
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablative Morphing
    # Predicts throat expansion and resulting pressure decay
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Supersonic Exit Velocity (Isentropic Flow Correction)
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Sec-to-Sec Sustainability & 100mm Refractory Lag
    # Uses Heat Balance Equation to determine Water LPM
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) # 100mm depth effect
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Margin of Safety per second
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Req. Coolant (L/s)": np.round(req_cooling_lps, 2),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Final Master Deployment")
# Fixed Developer and Version strings to avoid NameError
st.markdown("**Developer:** R. Puneesh kumar | **Version:** V-Max (Final Aerospace Deployment)")

with st.sidebar:
    st.header("1. HGG Propulsion Inputs")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain_in = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    
    st.header("2. JDD Wedge Configuration")
    jdd_angle = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)
    st.success("Universal Master Mode: ACTIVE")

# EXECUTE PHYSICS ENGINE
df, g_calc = run_vmax_final_twin(t_in, p_in, burn, water, grain_in, jdd_angle, cement)

# --- DYNAMIC FIRING VISUALIZATION ---
# Visualizes High-Resolution Spatial Mapping and plume interaction
st.subheader("🔥 Dynamic Plume Firing Visualization")
flame_intensity = p_in / 80
fig_fire = go.Figure()

# Nozzle Body (W-Cu Mixer)
fig_fire.add_trace(go.Scatter(x=[-1, 1
