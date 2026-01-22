import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Throat Erosion Master", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE SUPREME PHYSICS ENGINE (WITH EROSION) ---
def run_vmax_final_master(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth, ld_ratio, jdd_type, throat_dia_init):
    # Steel-Wall Guardrails
    duration = int(max(1, duration))
    p_init = float(max(1.1, p_init))
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. PREDICTION: Throat Erosion (W-Cu Mixer Logic)
    # Predicted radial erosion rate based on Temp and Pressure
    erosion_rate_base = (temp / 3032) * (p_init / 35) * 0.022 
    cumulative_erosion = erosion_rate_base * t_steps
    current_throat_dia = throat_dia_init + (2 * cumulative_erosion) 
    
    # 2. PREDICTION: Pressure Decay (Linked to Area Growth)
    area_ratio = (throat_dia_init**2) / (current_throat_dia**2)
    # Combined effect of Throat expansion and Paraffin fuel regression
    p_decay = p_init * area_ratio * np.power((np.maximum(grain_init - (0.55 * t_steps), 0.1) / grain_init), 0.15)
    
    # 3. PREDICTION: Gamma-DNA & Mach Number
    gamma_eff = np.clip(1.38 - (temp / 12500) + (ld_ratio * 0.004), 1.11, 1.45)
    g_minus_1 = max(0.001, gamma_eff - 1)
    p_exp = g_minus_1 / gamma_eff
    mach_num = np.sqrt(np.clip((2 / g_minus_1) * (np.power(p_decay / 1.01325, p_exp) - 1), 0, 10))
    
    # 4. PREDICTION: Acoustic Load (dB)
    R_spec = 518.6
    v_term = (2 * gamma_eff * R_spec * temp) / g_minus_1
    p_ratio_base = np.clip(1.05 / np.maximum(p_decay, 1.06), 0.0001, 0.999)
    v_exit = np.sqrt(np.clip(v_term * (1 - np.power(p_ratio_base, p_exp)), 0, 1e7))
    acoustic_db = 120 + 10 * np.log10(np.clip((v_exit**8) / 1e12, 1.0, 1e20))
    
    # 5. JDD SUSTAINABILITY (Transpiration)
    theta_rad = np.radians(jdd_theta)
    thermal_lag = 1.0 / (1.0 + (0.015 * max(0, cement_depth)))
    req_cooling_lps = np.clip(((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_lag, 0.001, 1000)
    actual_lps = float(h2o_lpm) / 60.0 if jdd_type == "Metallic Plate (Transpiration)" else 0.0
    mos = (actual_lps / req_cooling_lps) - 1.0

    return pd.DataFrame({
        "Sec": t_steps,
        "Throat Erosion (mm)": np.round(cumulative_erosion, 3),
        "Pressure (Bar)": np.round(p_decay, 2),
        "Mach Number": np.round(mach_num, 3),
        "Acoustic Load (dB)": np.round(acoustic_db, 1),
        "Sustainability (MoS)": np.round(mos, 3)
    }), cumulative_erosion[-1]

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Supreme All-In-One Master")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** Hyper-Hardened Erosion Mode")

with st.sidebar:
    st.header("1. HGG Design (Throat & L/D)")
    t_dia = st.number_input("Initial Throat Dia (mm)", 5.0, 50.0, 12.0)
    ld = st.slider("L/D Ratio", 1.5, 6.0, 3.5)
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    st.header("2. Material Sustainability")
    jdd_mat = st.selectbox("Impingement Surface", ["Metallic Plate (Transpiration)", "Pure Refractory Cement Wedge"])
    jdd_theta = st.slider("JDD Angle (°)", 15, 90, 35)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn_dur = st.number_input("Burn Duration (s)", 5, 120, 20)
    st.success("Universal Master Mode: ACTIVE")

# EXECUTE ENGINE
df, total_erosion = run_vmax_final_master(t_in, p_in, burn_dur, water, 30.0, jdd_theta, 100, ld, jdd_mat, t_dia)

# --- PREDICTION DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Throat Erosion", f"{total_erosion:.3f} mm")
c2.metric("Peak Acoustic Load", f"{df['Acoustic Load (dB)'].max()} dB")
c3.metric("Final Mach", f"M {df['Mach Number'].iloc[-1]}")
c4.metric("Sustainability MoS", f"{df['Sustainability (MoS)'].iloc[-1]}")

# --- ANALYTICS ---

st.subheader("📈 Temporal Sensor Analytics")
a1, a2, a3 = st.columns(3)
with a1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Throat Erosion (mm)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Throat Erosion (mm)", template="plotly_dark"))
with a2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Pressure Decay", template="plotly_dark"))
with a3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability MoS", template="plotly_dark"))

st.dataframe(df, use_container_width=True)
