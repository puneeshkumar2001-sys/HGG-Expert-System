import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- PHYSICS ENGINE ---
def run_vmax_final_master(target_f_n, duration, water_lpm, theta, t_dia_init):
    t_steps = np.arange(0, duration + 1, 1)
    at_init = (np.pi * (t_dia_init/1000)**2) / 4
    cf = 1.45
    p_req_bar = (target_f_n / (cf * at_init)) / 1e5
    
    results = []
    current_dia = t_dia_init
    for t in t_steps:
        area_ratio = (t_dia_init**2) / (current_dia**2)
        p_inst = p_req_bar * area_ratio
        rate = (3000/3032) * (p_inst/35) * 0.022
        current_dia += (2 * rate)
        req_lpm = ((p_inst * (3000/1050) * np.sin(np.radians(theta))) / 1.08) * 0.4 * 60
        
        results.append({
            "Sec": t,
            "Thrust (N)": round(target_f_n * area_ratio, 1),
            "Pressure (Bar)": round(p_inst, 2),
            "Erosion (mm)": round((current_dia - t_dia_init) / 2, 3),
            "Req. Water (LPM)": round(req_lpm, 1)
        })
    return pd.DataFrame(results), p_req_bar

# --- UI & OUTPUT ---
st.title("🚀 V-MAX Omni-Twin Master: 1.55 kN Mission")
df, p_start = run_vmax_final_master(1550, 20, 424, 45, 21.04)

st.subheader("📋 Second-by-Second Engineering Data")
st.table(df.iloc[[0, 5, 10, 15, 20]]) # Displaying key intervals

st.subheader("🛡️ JDD Tilt Sustainability Analysis")
if df['Req. Water (LPM)'].max() > 424:
    st.error(f"45° Angle requires {df['Req. Water (LPM)'].max()} LPM. AT 424 LPM, YOU MUST REDUCE TILT TO 11°.")
else:
    st.success("Configuration is sustainable at current flow.")
