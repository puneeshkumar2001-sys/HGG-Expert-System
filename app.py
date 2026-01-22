import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- WORLD-CLASS UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Realistic Firing Master", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE SUPREME PHYSICS ENGINE ---
def run_vmax_final_sim(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching (Real-Gas Correction)
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablative Morphing & Regression
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Supersonic Exit Velocity (Isentropic Flow)
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Sec-to-Sec Sustainability & 100mm Refractory
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 
    
    # 5. Acoustic Load (Lighthill's 8th Power Law)
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Acoustics (dB)": np.round(acoustic_db, 1),
        "Temp (K)": np.round(temp * (0.85 - 0.001 * t_steps), 0),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Final Master Deployment")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** World-Class Firing Simulation")

with st.sidebar:
    st.header("1. HGG Propulsion")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    st.header("2. 100mm Wedge Design")
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)

df, g_calc = run_vmax_final_sim(t_in, p_in, burn, water, grain, jdd_theta, cement)

# --- REALISTIC FIRING VISUALIZATION ---
st.subheader("🔥 High-Fidelity Exhaust Impingement Simulation")
flame_scale = (p_in / 80) + 0.3
fig_real = go.Figure()

# 1. Realistic Nozzle (Metallic W-Cu Mixer)
fig_real.add_trace(go.Scatter(x=[-0.6, 0.6, 0.4, -0.4, -0.6], y=[3, 3, 1, 1, 3], fill="toself", fillcolor='silver', line=dict(color='black'), name="W-Cu Nozzle"))

# 2. Supersonic Plume (Multi-Layer Fire Core)
# Core (Hotter white core)
fig_real.add_trace(go.Scatter(x=[-0.15*flame_scale, 0.15*flame_scale, 0.4*flame_scale, -0.4*flame_scale], y=[1, 1, -1.5*flame_scale, -1.5*flame_scale], fill="toself", fillcolor='white', opacity=0.9, showlegend=False))
# Outer Plume (Orange exhaust)
fig_real.add_trace(go.Scatter(x=[-0.3*flame_scale, 0.3*flame_scale, 1.2*flame_scale, -1.2*flame_scale], y=[1, 1, -2.5*flame_scale, -2.5*flame_scale], fill="toself", fillcolor='orange', opacity=0.6, name="Exhaust Plume"))

# 3. 100mm Refractory Wedge at 35 Degrees (Realistic Slab)
fig_real.add_trace(go.Scatter(x=[-3, 3, 3, -3], y=[-4, -3.5, -3.8, -4.3], fill="toself", fillcolor='brown', line=dict(color='darkred'), name="100mm Wedge"))

fig_real.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-5, 4], visible=False), height=400, template="plotly_dark")
st.plotly_chart(fig_real, use_container_width=True)

# --- INDEPENDENT SENSOR ANALYTICS (TIME-TO-TIME) ---
st.subheader("📈 High-Resolution Temporal Sensor Suite")
c1, c2, c3 = st.columns(3)
with c1:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Chamber Pressure vs Time", template="plotly_dark", yaxis_title="Bar"))
with c2:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Temp (K)'], line=dict(color='#ffa500', width=3))).update_layout(title="Stagnation Temp vs Time", template="plotly_dark", yaxis_title="Kelvin"))
with c3:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Acoustics (dB)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Acoustic Load vs Time", template="plotly_dark", yaxis_title="dB"))

c4, c5 = st.columns(2)
with c4:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Velocity (m/s)'], line=dict(color='#32cd32', width=3))).update_layout(title="Exit Velocity vs Time", template="plotly_dark", yaxis_title="m/s"))
with c5:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b', width=3))).update_layout(title="Global Sustainability Corridor (MoS)", template="plotly_dark", yaxis_title="Ratio"))

# --- DATA MATRIX ---
st.subheader("📊 Sec-to-Sec Sustainability Intelligence Matrix")
st.dataframe(df, use_container_width=True)
