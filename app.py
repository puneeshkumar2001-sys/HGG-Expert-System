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

# --- THE SUPREME PHYSICS ENGINE (HARDENED) ---
def run_vmax_final_master(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth, ld_ratio, jdd_type):
    # 1. CLIPPING & INPUT PROTECTION
    duration = max(1, int(duration))
    p_init = max(1.1, float(p_init))
    temp = max(300, float(temp))
    ld_ratio = max(1.0, float(ld_ratio))
    
    t_steps = np.arange(0, duration + 1, 1)
    
    # 2. GAMMA-DNA MATCHING (Guarded > 1.1 to prevent infinity)
    gamma_eff = np.clip(1.38 - (temp / 12500) + (ld_ratio * 0.004), 1.11, 1.45)
    R_spec = 518.6 
    
    # 3. PROPELLANT & CHAMBER PREDICTIONS
    reg_rate = 0.55 
    required_web = reg_rate * duration 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0.1)
    p_decay = p_init * (web_remaining / max(0.1, grain_init))**0.48
    grain_length = 15.5 * ld_ratio 
    gox_flow = (p_init * 0.02) * (1 + (ld_ratio / 10)) 
    
    # 4. ACOUSTIC & VELOCITY PREDICTIONS (CRASH PROTECTION)
    g_minus_1 = gamma_eff - 1
    # Guarding the v_term from blowing up to infinity
    v_term = (2 * gamma_eff * R_spec * temp) / g_minus_1
    p_exp = g_minus_1 / gamma_eff
    
    # Guarding the pressure ratio to stay within [0, 1]
    p_ratio_base = np.clip(1.05 / np.maximum(p_decay, 1.06), 0.0001, 0.999)
    p_ratio = np.power(p_ratio_base, p_exp)
    
    # Final sqrt protection: Ensure no Infinity and no Negative
    v_exit = np.sqrt(np.clip(v_term * (1 - p_ratio), 0, 1e7))
    
    # Acoustic dB calculation with Lighthill's Law
    acoustic_db = 120 + 10 * np.log10(np.clip((v_exit**8) / 1e12, 1.0, 1e20))
    
    # 5. JDD SUSTAINABILITY PREDICTIONS
    theta_rad = np.radians(jdd_theta)
    thermal_lag = 1 / (1 + (0.015 * cement_depth))
    turb_factor = 1.15 if ld_ratio < 2.5 else 1.0
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_lag * turb_factor
    
    actual_lps = h2o_lpm / 60 if jdd_type == "Metallic Plate (Transpiration)" else 0
    mos = (actual_lps / max(0.0001, req_cooling_lps)) - 1 if jdd_type == "Metallic Plate (Transpiration)" else 1

    mach_num = np.sqrt(np.clip((2 / g_minus_1) * (np.power(p_init / 1.01325, p_exp) - 1), 0, 25))

    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Mach Number": np.round(mach_num - (t_steps * 0.01), 3),
        "Acoustic Load (dB)": np.round(acoustic_db - (t_steps * 0.2), 1),
        "Req. Water (L/s)": np.round(req_cooling_lps, 2),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff, required_web, grain_length, gox_flow

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Supreme All-In-One Master")
st.markdown("**Developer:** R. Puneesh kumar | **Status:** Hardened Deployment Mode")

with st.sidebar:
    st.header("1. HGG Design (L/D Optimization)")
    ld = st.slider("L/D Ratio", 1.5, 6.0, 3.5)
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

# EXECUTE ENGINE
df, g_calc, req_web, g_len, g_flow = run_vmax_final_master(t_in, p_in, burn_dur, water, grain_user, jdd_theta, cement, ld, jdd_mat)

# --- PREDICTION DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Predicted Mach", f"M {df['Mach Number'].max()}")
c2.metric("Peak Acoustic", f"{df['Acoustic Load (dB)'].max()} dB")
c3.metric("Min Wax Web", f"{req_web:.1f} mm")
c4.metric("Peak GOx Flow", f"{g_flow:.2f} kg/s")

# --- REALISTIC VISUALIZATION ---

st.subheader(f"🔥 Realistic Firing: {jdd_mat} @ {jdd_theta}°")
flame_scale = (p_in / 80) + 0.3
fig_real = go.Figure()
fig_real.add_trace(go.Scatter(x=[-0.3*flame_scale, 0.3*flame_scale, 1.2*flame_scale, -1.2*flame_scale], y=[1, 1, -2.5*flame_scale, -2.5*flame_scale], fill="toself", fillcolor='orange', opacity=0.7, name="Exhaust"))
h_color = 'silver' if jdd_mat == "Metallic Plate (Transpiration)" else 'brown'
fig_real.add_trace(go.Scatter(x=[-3, 3], y=[-3.5, -3.0], line=dict(color=h_color, width=12 + (cement/10)), name="Impingement Point"))
if jdd_mat == "Metallic Plate (Transpiration)":
    fig_real.add_trace(go.Scatter(x=np.linspace(-2.5, 2.5, 10), y=np.linspace(-3.5, -3.0, 10)+0.2, mode='markers', marker=dict(color='#00d4ff', size=10), name="Water Sustain"))
fig_real.update_layout(xaxis=dict(range=[-4, 4], visible=False), yaxis=dict(range=[-6, 4], visible=False), height=400, template="plotly_dark")
st.plotly_chart(fig_real, use_container_width=True)

# --- ANALYTICS ---

st.subheader("📈 Temporal Sensor Analytics")
a1, a2, a3 = st.columns(3)
with a1: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Chamber Pressure vs Time", template="plotly_dark"))
with a2: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Acoustic Load (dB)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Acoustic Load vs Time", template="plotly_dark"))
with a3: st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability MoS", template="plotly_dark"))

st.dataframe(df, use_container_width=True)
