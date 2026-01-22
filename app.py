import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- WORLD-CLASS UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Global Gold Standard", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE "LEARNING BRAIN" PHYSICS ENGINE ---
def run_vmax_supreme_twin(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth, ld_ratio):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching & L/D Optimization 
    # L/D ratio affects stay time and combustion efficiency
    gamma_eff = 1.38 - (temp / 12500) + (ld_ratio * 0.004) 
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablative Morphing [cite: 12, 13]
    # Simulates real-time throat expansion of the W-Cu Mixer
    reg_rate = 0.55 # Paraffin regression rate (mm/s)
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Transpiration Cooling: JDD Sustainability 
    # Water pushed through metallic plate holes to block heat flux
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) # 100mm refractory lag effect
    
    # Heat Balance: Required Flow based on Oblique vs Normal Shock dynamics
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Sustainability Margin of Safety
    
    # 4. Acoustic Load (Lighthill's Law) 
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    # 5. Supersonic Velocity (Isentropic Expansion) 
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit * 0.982, 1),
        "Req. Coolant (L/s)": np.round(req_cooling_lps, 2),
        "Acoustics (dB)": np.round(acoustic_db, 1),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Most Advanced Master Model")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** World-Class Firing Simulation")

with st.sidebar:
    st.header("1. HGG Propulsion & L/D")
    ld = st.slider("L/D Ratio (Stay Time)", 1.5, 6.0, 3.5)
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    
    st.header("2. JDD Transpiration Shield")
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Burn Duration (s)", 5, 120, 20)
    st.success("Universal Deployment Mode: ACTIVE")

# EXECUTE MASTER ENGINE
df, g_calc = run_vmax_supreme_twin(t_in, p_in, burn, water, grain, jdd_theta, cement, ld)

# --- REAL-TIME FIRING VISUALIZATION ---
st.subheader(f"🔥 Realistic Firing at {jdd_theta}° (JDD Sustainability Active)")
flame_scale = (p_in / 80) + 0.3
fig_real = go.Figure()
# Nozzle & Plume
fig_real.add_trace(go.Scatter(x=[-0.6, 0.6, 0.4, -0.4, -0.6], y=[3, 3, 1, 1, 3], fill="toself", fillcolor='silver', name="Nozzle"))
fig_real.add_trace(go.Scatter(x=[-0.3*flame_scale, 0.3*flame_scale, 1.2*flame_scale, -1.2*flame_scale], y=[1, 1, -2.5*flame_scale, -2.5*flame_scale], fill="toself", fillcolor='orange', opacity=0.7, name="Plume"))
# JDD Plate with Transpiration Holes
angle_rad = np.radians(jdd_theta)
plate_x = np.array([-3, 3]); plate_y = np.array([-4, -4 + 6 * np.tan(angle_rad - np.radians(35))])
fig_real.add_trace(go.Scatter(x=plate_x, y=plate_y, line=dict(color='brown', width=12), name="JDD Metallic Plate"))
# Water Pushed through holes
fig_real.add_trace(go.Scatter(x=np.linspace(-2.5, 2.5, 10), y=np.linspace(plate_y[0], plate_y[1], 10)+0.2, mode='markers', marker=dict(color='#00d4ff', size=10), name="Coolant Holes"))
fig_real.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-6, 4], visible=False), height=400, template="plotly_dark")
st.plotly_chart(fig_real, use_container_width=True)

# --- INDEPENDENT ANALYTICS DASHBOARD ---
st.subheader("📊 Temporal Sensor Analytics (Time-to-Time)")
c1, c2, c3 = st.columns(3)
with c1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Pressure vs Time", template="plotly_dark"))
with c2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Req. Coolant (L/s)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Water Needed (L/s)", template="plotly_dark"))
with c3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability MoS", template="plotly_dark"))

# DATA MATRIX
st.subheader("📋 Decision Intelligence Matrix")
st.dataframe(df, use_container_width=True)
