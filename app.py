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

# --- THE SUPREME PHYSICS ENGINE ---
def run_vmax_supreme_master(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, ld_ratio, throat_dia_init):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Prediction: Gamma-DNA & Propellant Recipe
    gamma_eff = np.clip(1.38 - (temp / 12500) + (ld_ratio * 0.004), 1.11, 1.45)
    wax_length = 15.5 * ld_ratio
    wax_web_required = 0.55 * duration # mm
    gox_flow_req = (p_init * 0.022) * (1 + (ld_ratio / 12))
    
    # 2. Prediction: Throat Erosion (Iterative Logic)
    # This is why the result is ~0.474mm: the rate decays as pressure decays
    erosion_list = []
    p_list = []
    current_dia = throat_dia_init
    
    for t in t_steps:
        # Erosion rate depends on instantaneous pressure
        p_inst = p_init * (throat_dia_init**2 / current_dia**2)
        rate = (temp / 3032) * (p_inst / 35) * 0.022
        erosion_depth = rate * 1 # per second
        current_dia += (2 * erosion_depth)
        erosion_list.append((current_dia - throat_dia_init) / 2)
        p_list.append(p_inst)

    # 3. Prediction: Acoustic Load (Lighthill's Law)
    R_spec = 518.6
    g_m_1 = gamma_eff - 1
    v_term = (2 * gamma_eff * R_spec * temp) / g_m_1
    p_ratio = np.power(1.05 / np.array(p_list), g_m_1 / gamma_eff)
    v_exit = np.sqrt(np.clip(v_term * (1 - p_ratio), 0, 1e7))
    acoustic_db = 120 + 10 * np.log10(np.clip((v_exit**8) / 1e12, 1.0, 1e20))

    return pd.DataFrame({
        "Sec": t_steps,
        "Throat Erosion (mm)": np.round(erosion_list, 3),
        "Chamber Pressure (Bar)": np.round(p_list, 2),
        "Acoustic Load (dB)": np.round(acoustic_db, 1),
        "Mach Number": np.round(np.sqrt((2/g_m_1)*((p_init/1.01)**(g_m_1/gamma_eff)-1)) - (t_steps*0.01), 3)
    }), gamma_eff, wax_length, wax_web_required, gox_flow_req

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Design & Firing Expert")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** Iterative Physics Mode")

with st.sidebar:
    st.header("1. HGG Optimization")
    ld = st.slider("L/D Ratio", 1.5, 6.0, 3.01)
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3000)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    t_dia = st.number_input("Initial Throat Dia (mm)", 5.0, 50.0, 21.04)
    
    st.header("2. JDD & Cooling")
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 45)
    water = st.number_input("Water Supply (LPM)", 100, 1500, 424)
    burn_dur = st.number_input("Burn Duration (s)", 5, 120, 20)

# EXECUTE ENGINE
df, g_dna, w_len, w_web, g_flow = run_vmax_supreme_master(t_in, p_in, burn_dur, water, 30.0, jdd_theta, ld, t_dia)

# --- RESULTS DASHBOARD ---
st.subheader("📋 Predicted Design Recipe")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Gamma-DNA (γ)", f"{g_dna:.3f}")
r2.metric("Paraffin Length", f"{w_len:.1f} mm")
r3.metric("Min Wax Web", f"{w_web:.1f} mm")
r4.metric("GOx Flow Req.", f"{g_flow:.3f} kg/s")

# --- FIRING VISUALIZATION ---

st.subheader("🔥 Firing Visualization: Plume-JDD Interaction")
fig = go.Figure()
# Nozzle & Plume
fig.add_trace(go.Scatter(x=[0, 1, 2.5, -2.5, -1, 0], y=[4, 3.5, 0.5, 0.5, 3.5, 4], fill="toself", fillcolor='orange', name="Exhaust Plume"))
# JDD Surface at 45 Degrees
fig.add_trace(go.Scatter(x=[-4, 4], y=[-0.5, -2.5], line=dict(color='silver', width=10), name="JDD Metallic Plate"))
fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), template="plotly_dark", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- ANALYTICS ---

st.subheader("📈 Digital Performance Verification")
a1, a2, a3 = st.columns(3)
with a1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Chamber Pressure (Bar)'], line=dict(color='#ff4b4b'))).update_layout(title="Pressure Decay", template="plotly_dark"))
with a2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Throat Erosion (mm)'], line=dict(color='#00d4ff'))).update_layout(title="Iterative Throat Erosion", template="plotly_dark"))
with a3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Acoustic Load (dB)'], line=dict(color='#f0c14b'))).update_layout(title="Acoustic Fatigue (dB)", template="plotly_dark"))

st.dataframe(df, use_container_width=True)
