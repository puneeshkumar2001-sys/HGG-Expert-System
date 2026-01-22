import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | JDD Sustainability", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE SUPREME PHYSICS ENGINE ---
def run_vmax_supreme_master(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, ld_ratio, throat_dia_init, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Reverse-Design: Gamma & Propellant Recipe
    gamma_eff = np.clip(1.38 - (temp / 12500) + (ld_ratio * 0.004), 1.11, 1.45)
    wax_length = 15.5 * ld_ratio
    wax_web_required = 0.55 * duration 
    gox_flow_req = (p_init * 0.022) * (1 + (ld_ratio / 12))
    
    # 2. Iterative Throat Erosion & Pressure Decay
    erosion_list = []
    p_list = []
    current_dia = throat_dia_init
    for t in t_steps:
        p_inst = p_init * (throat_dia_init**2 / current_dia**2)
        rate = (temp / 3032) * (p_inst / 35) * 0.022
        current_dia += (2 * rate)
        erosion_list.append((current_dia - throat_dia_init) / 2)
        p_list.append(p_inst)

    # 3. JDD Sustainability (Transpiration Cooling Prediction)
    theta_rad = np.radians(jdd_theta)
    thermal_lag = 1.0 / (1.0 + (0.015 * cement_depth))
    # Formula predicts required water to block heat flux at impingement
    req_lps_list = [((p * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_lag for p in p_list]
    req_lpm_max = max(req_lps_list) * 60
    
    # Margin of Safety (MoS) based on user's current flow (424 LPM)
    actual_lps = h2o_lpm / 60
    mos_list = [(actual_lps / req) - 1 for req in req_lps_list]

    # 4. Acoustic Load
    R_spec = 518.6
    g_m_1 = gamma_eff - 1
    v_term = (2 * gamma_eff * R_spec * temp) / g_m_1
    p_ratio = np.power(1.05 / np.array(p_list), g_m_1 / gamma_eff)
    v_exit = np.sqrt(np.clip(v_term * (1 - p_ratio), 0, 1e7))
    acoustic_db = 120 + 10 * np.log10(np.clip((v_exit**8) / 1e12, 1.0, 1e20))

    return pd.DataFrame({
        "Sec": t_steps,
        "Throat Erosion (mm)": np.round(erosion_list, 3),
        "Pressure (Bar)": np.round(p_list, 2),
        "Req. Water (LPM)": np.round(np.array(req_lps_list) * 60, 1),
        "Acoustic Load (dB)": np.round(acoustic_db, 1),
        "Sustainability (MoS)": np.round(mos_list, 3)
    }), gamma_eff, wax_length, wax_web_required, gox_flow_req, req_lpm_max

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Design, Erosion & Sustainability Master")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** JDD Sustainability Active")

with st.sidebar:
    st.header("1. HGG Design Optimization")
    ld = st.slider("L/D Ratio", 1.5, 6.0, 3.01)
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3000)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    t_dia = st.number_input("Initial Throat Dia (mm)", 5.0, 50.0, 21.04)
    
    st.header("2. JDD Sustainability")
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 45)
    cement = st.slider("Refractory Depth (mm)", 0, 200, 100)
    water = st.number_input("Your Water Flow (LPM)", 100, 2000, 424)
    burn_dur = st.number_input("Burn Duration (s)", 5, 120, 20)

# EXECUTE ENGINE
df, g_dna, w_len, w_web, g_flow, water_req = run_vmax_supreme_master(t_in, p_in, burn_dur, water, 30.0, jdd_theta, ld, t_dia, cement)

# --- RESULTS DASHBOARD ---
st.subheader("🔮 Predicted Design & Sustainability Requirements")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Gamma-DNA (γ)", f"{g_dna:.3f}")
r2.metric("Paraffin Length", f"{w_len:.1f} mm")
r3.metric("GOx Flow Req.", f"{g_flow:.3f} kg/s")
# This is the most important result for your question
r4.metric("REQUIRED WATER", f"{water_req:.0f} LPM", delta=f"{water - water_req:.0f} LPM Surplus", delta_color="inverse")

# --- FIRING VISUALIZATION ---

st.subheader("🔥 Firing Visualization: Plume-JDD Sustainability")
fig = go.Figure()
fig.add_trace(go.Scatter(x=[0, 1, 2.5, -2.5, -1, 0], y=[4, 3.5, 0.5, 0.5, 3.5, 4], fill="toself", fillcolor='orange', name="Exhaust Plume"))
fig.add_trace(go.Scatter(x=[-4, 4], y=[-0.5, -2.5], line=dict(color='silver', width=10), name="Metallic JDD Plate"))
if water < water_req:
    st.error(f"⚠️ DANGER: Current flow {water} LPM is BELOW required {water_req:.0f} LPM for {jdd_theta}° angle!")
else:
    st.success(f"✅ SUSTAINABLE: Current flow {water} LPM protects the plate.")

fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- ANALYTICS ---

st.subheader("📈 Digital Performance Analytics")
a1, a2, a3 = st.columns(3)
with a1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Req. Water (LPM)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Water Needed (LPM) vs Time", template="plotly_dark"))
with a2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Throat Erosion (mm)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Erosion Progression", template="plotly_dark"))
with a3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability MoS", template="plotly_dark"))

st.dataframe(df, use_container_width=True)
