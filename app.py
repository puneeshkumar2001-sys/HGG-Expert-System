import streamlit as st
import numpy as np
import pandas as pd

# --- HGG EXPERT CALCULATIONS ---
def calculate_expert_metrics(gamma, mach, temp, duration, velocity=1200):
    # 1. Acoustic Power (Sound Pressure Level)
    # Sound increases with Velocity^8
    db_level = 10 * np.log10(velocity**8) - 40 
    
    # 2. Pressure Oscillations (Stability)
    # Higher pressure and Mach usually increase vibration risk
    vibration_risk = (mach * 0.15) + (temp / 4000)
    
    # 3. Heat Flux (Thermal Load)
    # q = h * (T_gas - T_wall) -> Simplified
    heat_flux = (temp * 0.002) * (mach**0.8) # MW/m2
    
    return db_level, vibration_risk, heat_flux

# --- In your Streamlit UI section, add these new displays ---
st.divider()
st.subheader("📊 Dynamic Expert Analysis")

db, vib, q = calculate_expert_metrics(w_gamma, w_mach, tmp, w_dur)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Acoustic Load", f"{db:.1f} dB")
col_b.metric("Vibration Index", f"{vib:.2f}")
col_c.metric("Heat Flux", f"{q:.2f} MW/m²")

# Safety Warnings
if db > 155:
    st.error("🚨 HIGH NOISE: Structural fatigue risk for JDD.")
if q > 5.0:
    st.warning("⚠️ THERMAL LIMIT: Increase transpiration coolant flow immediately!")

# --- UI DESIGN ---
st.title("🚀 HGG Expert Guru")
st.write("Design your HGG to match CH4/LOX for JDD Testing.")

# Sliders
w_gamma = st.sidebar.slider("Target Gamma (γ)", 1.15, 1.30, 1.21)
w_mach = st.sidebar.slider("Target Mach (M)", 0.5, 3.0, 1.5)
w_dur = st.sidebar.number_input("Test Duration (s)", 10, 300, 60)

# Results
sof, tmp, ar, thk = calculate_hgg(w_gamma, w_mach, w_dur)

st.metric("Suggested O/F Ratio", f"{sof:.2f}")
st.metric("Nozzle Area Ratio", f"{ar:.2f}")
st.metric("Gas Temp", f"{tmp:.0f} K")
st.info(f"Required Fuel Thickness: {thk*1000:.1f} mm")
