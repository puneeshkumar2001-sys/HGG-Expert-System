import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Master Blaster", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- PHYSICS & COMPARISON ENGINE ---
def run_vmax_master_engine(target_f_n, duration, water_lpm, theta, t_dia_init):
    t_steps = np.arange(0, duration + 1, 1)
    
    # Anchor: Required Pressure for 1.55 kN
    # F = Cf * Pc * At
    at_init = (np.pi * (t_dia_init/1000)**2) / 4
    cf = 1.45
    p_req_bar = (target_f_n / (cf * at_init)) / 1e5
    
    # Simulation Loops
    results = []
    current_dia = t_dia_init
    
    for t in t_steps:
        # Pressure decay due to throat area growth
        area_ratio = (t_dia_init**2) / (current_dia**2)
        p_inst = p_req_bar * area_ratio
        
        # Iterative Scouring Rate (W-Cu Mixer at 3000K)
        rate = (3000/3032) * (p_inst/35) * 0.022
        current_dia += (2 * rate)
        
        # Sustainability & Acoustics
        req_lpm = ((p_inst * (3000/1050) * np.sin(np.radians(theta))) / 1.08) * 0.4 * 60
        ve = 2850 # Exit Velocity (m/s)
        # Lighthill's 8th Power Law
        db = 120 + 10 * np.log10(np.clip((ve**8) / 1e12, 1.0, 1e20))
        
        results.append({
            "Sec": t,
            "Thrust (N)": target_f_n * area_ratio,
            "Erosion (mm)": (current_dia - t_dia_init) / 2,
            "Pressure (Bar)": p_inst,
            "Req. Water (LPM)": req_lpm,
            "Acoustic (dB)": db
        })
        
    return pd.DataFrame(results), p_req_bar

# --- INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: 1.55 kN Master Blaster")
st.markdown("**Status:** Requirement-Driven Architecture Active")

with st.sidebar:
    st.header("🎯 Mission Requirements")
    f_target = st.number_input("Target Thrust (N)", value=1550)
    t_init = st.number_input("Initial Throat (mm)", value=21.04)
    st.header("🌊 Facility Limits")
    water_in = st.number_input("Water Flow (LPM)", value=424)
    theta_in = st.slider("JDD Angle (°)", 0, 90, 45)
    
df, p_start = run_vmax_master_engine(f_target, 20, water_in, theta_in, t_init)

# --- VISUALIZATION: FIRING & ACOUSTICS ---
col_vis, col_metric = st.columns([2, 1])

with col_vis:
    st.subheader("🔥 Firing & Acoustic Stress Interaction")
    fig = go.Figure()
    # Plume Path (45 Degree Impact)
    fig.add_trace(go.Scatter(x=[0, 1, 3, -3, -1, 0], y=[5, 4, 1, 1, 4, 5], fill="toself", fillcolor='orange', name="Plume"))
    # JDD Plate
    fig.add_trace(go.Scatter(x=[-5, 5], y=[0.5, -1.5], line=dict(color='silver', width=12), name="JDD Plate"))
    # Acoustic Vibration Zone
    fig.add_trace(go.Scatter(x=[-6, 6, 6, -6], y=[6, 6, -3, -3], fill="toself", opacity=0.1, fillcolor="blue", name="Acoustic Load"))
    fig.update_layout(template="plotly_dark", height=400, showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True)

with col_metric:
