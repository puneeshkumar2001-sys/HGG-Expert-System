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
def run_vmax_final_twin(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching (Real-Gas Correction) [cite: 11]
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablation & Paraffin Regression 
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Supersonic Exit Velocity (1.8% Viscous Correction) 
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Sec-to-Sec Sustainability & 100mm Refractory Lag 
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Margin of Safety per second [cite: 15]
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Req. Coolant (L/s)": np.round(req_cooling_lps, 2),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Final Master Deployment")
st.markdown(f"**Developer:** R. Puneesh kumar | **Version:** V-Max (Final Aerospace Deployment)") [cite: 2, 3]

with st.sidebar:
    st.header("1. HGG Propulsion")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain_in = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    
    st.header("2. Facility & 100mm Wedge")
    jdd_angle = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)
    st.success("Universal Master Mode: ACTIVE")

df, g_calc = run_vmax_final_twin(t_in, p_in, burn, water, grain_in, jdd_angle, cement)

# --- REAL-TIME FIRING VISUALIZATION ---
st.subheader("🔥 Dynamic Plume Firing Visualization")
flame_intensity = p_in / 80
fig_fire = go.Figure()
# Nozzle Body
fig_fire.add_trace(go.Scatter(x=[-1, 1, 0.5, -0.5, -1], y=[2, 2, 1, 1, 2], fill="toself", fillcolor='gray', line=dict(color='black'), name="W-Cu Mixer"))
# Exhaust Firing (Plume)
fig_fire.add_trace(go.Scatter(x=[-0.3*flame_intensity, 0.3*flame_intensity, 1.5*flame_intensity, -1.5*flame_intensity, -0.3*flame_intensity], 
                              y=[1, 1, -3*flame_intensity, -3*flame_intensity, 1], fill="toself", 
                              fillcolor='orange', opacity=0.8, line=dict(color='red'), name="Supersonic Plume"))
# 35 Degree JDD Wedge (Wedge at -3 on Y-axis)
fig_fire.add_trace(go.Scatter(x=[-3, 3, 3, -3], y=[-3.5, -3, -3, -3.5], fill="toself", fillcolor='brown', name="100mm Wedge"))
fig_fire.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-5, 3], visible=False), 
                       height=350, margin=dict(l=0, r=0, t=0, b=0), template="plotly_dark", showlegend=False)
st.plotly_chart(fig_fire, use_container_width=True)

# --- PERFORMANCE DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma-DNA (γ)", f"{g_calc:.3f}") [cite: 10, 11]
c2.metric("Max Velocity", f"{df['Velocity (m/s)'].max()} m/s") [cite: 18]
c3.metric("Peak Flow Needed", f"{df['Req. Coolant (L/s)'].max()} L/s") [cite: 18]
c4.metric("Min Safety Margin", f"{df['Sustainability (MoS)'].min():.2%}") [cite: 15]

st.divider()

# --- SEC-TO-SEC ANALYTICS ---
st.subheader("📊 Sec-to-Sec Sustainability Matrix")
st.dataframe(df, use_container_width=True)

# SENSOR ANALYTICS
r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Chamber Pressure (Ablative Morphing)", template="plotly_dark", yaxis_title="Bar")) [cite: 13]
with r2:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Safety Corridor (MoS)", template="plotly_dark", yaxis_title="Ratio")) [cite: 15]
