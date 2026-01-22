import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- ELITE UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Sustainability Edition", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- THE SUPREME PHYSICS ENGINE ---
def run_vmax_sustainability_twin(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching (Real-Gas Correction)
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Living Hardware: Ablation & Paraffin Regression 
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Supersonic Exit Velocity (1.8% Viscous Correction) 
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Sec-to-Sec Sustainability Calculation 
    # Heat Balance: Required Water LPM to block heat flux impingement
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    # Margin of Safety (MoS) per second
    mos = (actual_lps / req_cooling_lps) - 1 
    
    # 5. Acoustic Load (Lighthill's Law) 
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Req. Coolant (L/s)": np.round(req_cooling_lps, 2),
        "Acoustic (dB)": np.round(acoustic_db, 1),
        "Sustainability (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Sustainability Master Guru")
st.markdown(f"**Developer:** R. Puneesh kumar | **Version:** V-Max Final Deployment")

with st.sidebar:
    st.header("1. HGG Propulsion")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain_in = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    
    st.header("2. Facility & 100mm Wedge")
    jdd_angle = st.slider("JDD Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)
    st.success("Universal Sustainability Mode: ACTIVE")

# EXECUTE MASTER ENGINE
df, g_calc = run_vmax_sustainability_twin(t_in, p_in, burn, water, grain_in, jdd_angle, cement)

# --- GLOBAL PERFORMANCE DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma-DNA (γ)", f"{g_calc:.3f}")
c2.metric("Max Velocity", f"{df['Velocity (m/s)'].max()} m/s")
c3.metric("Peak Flow Needed", f"{df['Req. Coolant (L/s)'].max()} L/s")
c4.metric("Min Safety Margin", f"{df['Sustainability (MoS)'].min():.2%}")

st.divider()

# --- SEC-TO-SEC SUSTAINABILITY MATRIX ---
st.subheader("📊 Sec-to-Sec Sustainability Matrix")
st.dataframe(df, use_container_width=True)

# VISUAL ANALYTICS
r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Req. Coolant (L/s)'], line=dict(color='#00d4ff', width=3))).update_layout(title="Required Coolant vs Time", template="plotly_dark", yaxis_title="L/s"))
with r2:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Sustainability (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Sustainability Margin of Safety (MoS)", template="plotly_dark", yaxis_title="Ratio"))

# PDF EXPORT
def generate_pdf(data_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story, styles = [], getSampleStyleSheet()
    story.append(Paragraph("V-MAX MASTER SUSTAINABILITY REPORT", styles['Title']))
    story.append(Paragraph("Developer: R. Puneesh kumar", styles['Normal']))
    story.append(Spacer(1, 12))
    table_data = [data_df.columns.tolist()] + data_df.values.tolist()
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0c14b")), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    story.append(t)
    doc.build(story)
    return buffer.getvalue()

st.download_button("📥 Download Technical Defense PDF", data=generate_pdf(df), file_name="VMAX_Sustainability_Report.pdf")
