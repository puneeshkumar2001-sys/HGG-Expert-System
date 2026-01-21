import streamlit as st
import numpy as np
import pandas as pd

# --- HGG EXPERT CALCULATIONS ---
def calculate_hgg(gamma, mach, duration):
    sof = 1.0 + (gamma - 1.15) / 0.04
    temp = 1500 + (sof * 400)
    term1 = (2 / (gamma + 1))
    term2 = 1 + ((gamma - 1) / 2) * (mach**2)
    power = (gamma + 1) / (2 * (gamma - 1))
    area_ratio = (1 / mach) * (term1 * term2)**power
    thickness = 0.0002 * duration
    return sof, temp, area_ratio, thickness

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
