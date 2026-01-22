import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- FACILITY UI ---
st.title("🚀 V-MAX Static Test Assembly")
st.markdown("#### Components: HGG Motor (Paraffin) | Umbilical Tower | JDD Interface [cite: 1, 5]")

with st.sidebar:
    st.header("Component Specs")
    t_goal = st.slider("Chamber Temp (K)", 1500, 3500, 3032) #
    p_start = st.slider("Initial Pressure (Bar)", 10, 80, 35) #
    w_cu = st.slider("W-Cu Mixer (% Tungsten)", 50, 95, 75)
    burn_time = st.number_input("Burn Duration (s)", 5, 60, 20)

# Transient Physics Engine (Sec-to-Sec) [cite: 12, 13]
time = np.arange(0, burn_time + 1, 1)
p_series = p_start * np.exp(-0.01 * time) # Pressure Decay 
acoustic_db = (10 * np.log10((t_goal/10)**4) + 120) - (0.5 * time) # Acoustic Mapping 

# --- 3D COMPONENT INTERACTION VIEW ---
st.subheader("🔥 Live Firing: Motor-to-JDD Interaction")
col_vis, col_data = st.columns([2, 1])

with col_vis:
    # 3D Stagnation Point on JDD 
    x, y = np.linspace(-10, 10, 30), np.linspace(-10, 10, 30)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    Z = (t_goal / 10) * np.exp(-0.3 * R) * (p_series[-1] / p_start)
    
    fig = go.Figure(data=[go.Surface(z=Z, colorscale='Hot', name='JDD Surface')])
    fig.update_layout(title="JDD Thermal Gradient (Stagnation Point) ", 
                      template="plotly_dark", margin=dict(l=0, r=0, b=0, t=40))
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.metric("Umbilical Status", "CONNECTED [cite: 21]")
    st.metric("Peak Acoustic Load", f"{np.max(acoustic_db):.1f} dB ")
    st.write("Sec-to-Sec Chamber Pressure ")
    st.line_chart(p_series)

st.divider()
st.info("The V-MAX Guru manages the entire lifecycle—from O/F balancing to structural calibration[cite: 7].")
