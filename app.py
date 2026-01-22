import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io

# --- WORLD-CLASS UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Sensor Analytics", layout="wide")
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
    
    # 1. Gamma-DNA Matching (Real-Gas Correction) [cite: 10, 11]
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablative Morphing [cite: 12, 13]
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Supersonic Exit Velocity (Isentropic Flow Correction) 
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Sec-to-Sec Sustainability & 100mm Refractory Lag 
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Margin of Safety
    
    # 5. Acoustic Load (Lighthill's Law) 
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    # 6. Surface Stagnation Temperature (Degrades slightly over time)
    surf_temp = temp * (0.88 - (0.002 * t_steps))
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Temp (K)": np.round(surf_temp, 0),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Acoustics (dB)": np.round(acoustic_db, 1),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Master: Sensor Analytics Edition")
st.markdown("**Developer:** R. Puneesh kumar | **Version:** V-Max (Final Deployment)")

with st.sidebar:
    st.header("1. HGG Propulsion")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    st.header("2. 100mm Wedge Design")
    jdd_angle = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)

df, g_calc = run_vmax_final_twin(t_in, p_in, burn, water, grain, jdd_angle, cement)

# --- REAL-TIME FIRING VISUALIZATION ---
st.subheader("🔥 Dynamic Plume Interaction (SolidWorks Logic)")
flame_intensity = p_in / 80
fig_fire = go.Figure()
fig_fire.add_trace(go.Scatter(x=[-1, 1, 0.5, -0.5, -1], y=[2, 2, 1, 1, 2], fill="toself", fillcolor='gray', name="Mixer"))
fig_fire.add_trace(go.Scatter(x=[-0.3*flame_intensity, 0.3*flame_intensity, 1.5*flame_intensity, -1.5*flame_intensity, -0.3*flame_intensity], 
                              y=[1, 1, -3*flame_intensity, -3*flame_intensity, 1], fill="toself", fillcolor='orange', name="Plume"))
fig_fire.add_trace(go.Scatter(x=[-3, 3, 3, -3], y=[-3.5, -3, -3, -3.5], fill="toself", fillcolor='brown', name="100mm Wedge"))
fig_fire.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-5, 3], visible=False), height=300, template="plotly_dark", showlegend=False)
st.plotly_chart(fig_fire, use_container_width=True)

# --- INDIVIDUAL SENSOR ANALYTICS (TIME-TO-TIME) ---
st.subheader("📈 Independent Temporal Sensor Graphs")

# PRESSURE & TEMPERATURE
c1, c2 = st.columns(2)
with c1:
    fig_p = go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3)))
    fig_p.update_layout(title="Chamber Pressure vs Time", template="plotly_dark", yaxis_title="Bar")
    st.plotly_chart(fig_p, use_container_width=True)
with c2:
    fig_t = go.Figure(go.Scatter(x=df['Sec'], y=df['Temp (K)'], line=dict(color='#ffa500', width=3)))
    fig_t.update_layout(title="Stagnation Temp vs Time", template="plotly_dark", yaxis_title="Kelvin")
    st.plotly_chart(fig_t, use_container_width=True)

# ACOUSTICS & VELOCITY
c3, c4 = st.columns(2)
with c3:
    fig_a = go.Figure(go.Scatter(x=df['Sec'], y=df['Acoustics (dB)'], line=dict(color='#00d4ff', width=3)))
    fig_a.update_layout(title="Acoustic Load vs Time", template="plotly_dark", yaxis_title="dB")
    st.plotly_chart(fig_a, use_container_width=True)
with c4:
    fig_v = go.Figure(go.Scatter(x=df['Sec'], y=df['Velocity (m/s)'], line=dict(color='#32cd32', width=3)))
    fig_v.update_layout(title="Exit Velocity vs Time", template="plotly_dark", yaxis_title="m/s")
    st.plotly_chart(fig_v, use_container_width=True)

# SUSTAINABILITY MARGIN
st.divider()
fig_mos = go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b', width=4)))
fig_mos.update_layout(title="Structural Sustainability Corridor (MoS)", template="plotly_dark", yaxis_title="Ratio")
st.plotly_chart(fig_mos, use_container_width=True)

# DATA MATRIX
st.subheader("📊 Sec-to-Sec Sustainability Matrix")
st.dataframe(df, use_container_width=True)
