import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Supreme Master", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE "LEARNING BRAIN" PHYSICS ENGINE ---
def run_vmax_supreme_master(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth, ld_ratio, jdd_type):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Prediction: Gamma-DNA & Mach Number (Isentropic Flow)
    gamma_eff = 1.38 - (temp / 12500) + (ld_ratio * 0.004) 
    R_spec = 518.6 
    mach_num = np.sqrt((2 / (gamma_eff - 1)) * ((p_init / 1.01325)**((gamma_eff - 1) / gamma_eff) - 1))
    
    # 2. Prediction: Propellant Architecture (Paraffin Wax)
    reg_rate = 0.55 # mm/s
    required_web = reg_rate * duration 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    grain_length = 15.5 * ld_ratio 
    
    # 3. Prediction: GOx Flow Requirements
    gox_flow = (p_init * 0.02) * (1 + (ld_ratio / 10)) 
    
    # 4. Transpiration Cooling: JDD Sustainability (Jet Deflection Duct)
    theta_rad = np.radians(jdd_theta)
    thermal_lag = 1 / (1 + (0.015 * cement_depth)) if cement_depth > 0 else 1
    # Turbulence factor increases cooling need at low L/D
    turb_factor = 1.15 if ld_ratio < 2.5 else 1.0
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_lag * turb_factor
    actual_lps = h2o_lpm / 60 if jdd_type == "Metallic Plate (Transpiration)" else 0
    mos = (actual_lps / req_cooling_lps) - 1 if req_cooling_lps > 0 else 1

    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Mach Number": np.round(mach_num - (t_steps * 0.01), 3),
        "Req. GOx (kg/s)": np.round(gox_flow * (p_decay / p_init), 3),
        "Req. Water (L/s)": np.round(req_cooling_lps, 2),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff, required_web, grain_length

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Supreme Global Master")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** Autonomous Engineering Brain")

with st.sidebar:
    st.header("1. HGG Design (L/D Optimization)")
    ld = st.slider("L/D Ratio (Stay Time)", 1.5, 6.0, 3.5)
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    
    st.header("2. JDD Sustainability Hardware")
    grain_user = st.slider("Paraffin Initial Web (mm)", 10, 60, 30)
    jdd_mat = st.selectbox("Impingement Surface", ["Metallic Plate (Transpiration)", "Pure Refractory Cement Wedge"])
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 0, 150, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn_dur = st.number_input("Burn Duration (s)", 5, 120, 20)
    st.success("Universal Master Mode: ACTIVE")

# EXECUTE SUPREME ENGINE
df, g_calc, req_web, g_len = run_vmax_supreme_master(t_in, p_in, burn_dur, water, grain_user, jdd_theta, cement, ld, jdd_mat)

# --- PREDICTION DASHBOARD ---
st.subheader("🔮 Supreme Design Recipe")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Predicted Mach Number", f"M {df['Mach Number'].max()}")
c2.metric("Min Wax Web Required", f"{req_web:.1f} mm")
c3.metric("Predicted Grain Length", f"{g_len:.1f} mm")
c4.metric("Peak GOx Flow Required", f"{df['Req. GOx (kg/s)'].max()} kg/s")

# --- REALISTIC FIRING VISUALIZATION ---

st.subheader(f"🔥 Firing Simulation: {jdd_mat} @ {jdd_theta}°")
flame_scale = (p_in / 80) + 0.3
fig_real = go.Figure()
# Exhaust Plume
fig_real.add_trace(go.Scatter(x=[-0.3*flame_scale, 0.3*flame_scale, 1.2*flame_scale, -1.2*flame_scale], y=[1, 1, -2.5*flame_scale, -2.5*flame_scale], fill="toself", fillcolor='orange', opacity=0.7, name="Exhaust"))
# Hardware Surface
h_color = 'silver' if jdd_mat == "Metallic Plate (Transpiration)" else 'brown'
fig_real.add_trace(go.Scatter(x=[-3, 3], y=[-3.5, -3.0], line=dict(color=h_color, width=12 + (cement/10)), name="Impingement Point"))
# Coolant Holes (Transpiration)
if jdd_mat == "Metallic Plate (Transpiration)":
    fig_real.add_trace(go.Scatter(x=np.linspace(-2.5, 2.5, 10), y=np.linspace(-3.5, -3.0, 10)+0.2, mode='markers', marker=dict(color='#00d4ff', size=10), name="Coolant Flow"))
fig_real.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-6, 4], visible=False), height=400, template="plotly_dark")
st.plotly_chart(fig_real, use_container_width=True)

# --- ANALYTICS ---

st.subheader("📈 Temporal Design Analytics (Time-to-Time)")
a1, a2, a3 = st.columns(3)
with a1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Chamber Pressure vs Time", template="plotly_dark"))
with a2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Req. Water (L/s)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Required Water Needed (L/s)", template="plotly_dark"))
with a3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability Corridor (MoS)", template="plotly_dark"))

st.dataframe(df, use_container_width=True)
