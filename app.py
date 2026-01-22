import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- WORLD-CLASS UI STYLING ---
st.set_page_config(page_title="V-MAX Omni-Twin | Global Gold Standard", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0d10; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: bold; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- PHYSICS ENGINE: THE "LEARNING BRAIN" ---
def run_vmax_final_twin(temp, p_init, duration, h2o_lpm, grain_init, jdd_theta, cement_depth):
    t_steps = np.arange(0, duration + 1, 1)
    
    # 1. Gamma-DNA Matching [cite: 10, 11]
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Ablative Morphing (Throat Expansion Logic) [cite: 12, 13]
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Isentropic Flow Theory: Supersonic Expansion 
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Heat Balance: Transpiration & 100mm Refractory
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Margin of Safety 
    
    # 5. Acoustic Loading (Lighthill's Law) 
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Acoustic (dB)": np.round(acoustic_db, 1),
        "Safety Margin (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: Final Aerospace Expert System")
st.markdown(f"**Developer:** R. Puneesh kumar [cite: 2] | **Version:** {st.secrets.get('VERSION', 'V-Max Final')}")

# --- REPORT CONSTANTS SECTION ---
with st.expander("📖 View Executive Summary Constants (Based on Technical Report)"):
    st.write("**Elite Pillar 1:** Gamma-DNA Matching targets ~1.21 for high-fidelity expansion[cite: 11].")
    st.write("**Elite Pillar 2:** Real-Time Ablative Morphing predicts throat expansion[cite: 12, 13].")
    st.write("**Elite Pillar 3:** High-Resolution Spatial Mapping identifies Hot Spots[cite: 14].")

with st.sidebar:
    st.header("1. HGG Propulsion")
    t_in = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    p_in = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    grain = st.slider("Initial Fuel Web (mm)", 10, 60, 30)
    
    st.header("2. Facility & 100mm Wedge")
    jdd_angle = st.slider("JDD Tilt Angle (°)", 15, 90, 35)
    cement = st.slider("Refractory Depth (mm)", 10, 100, 100)
    water = st.number_input("Water Flow (LPM)", 100, 1500, 424)
    burn = st.number_input("Duration (s)", 5, 120, 20)
    st.success("Universal Master Mode: ACTIVE")

df, g_calc = run_vmax_final_twin(t_in, p_in, burn, water, grain, jdd_angle, cement)

# --- VISUAL FIRING INDICATOR (THE "FLAME") ---
st.subheader("🔥 Real-Time Motor Firing Visualization")
flame_intensity = p_in / 80
fig_flame = go.Figure()
# Nozzle shape
fig_flame.add_trace(go.Scatter(x=[-1, 1, 0.5, -0.5, -1], y=[2, 2, 1, 1, 2], fill="toself", fillcolor='gray', line=dict(color='black'), name="W-Cu Mixer"))
# Dynamic Plume
fig_flame.add_trace(go.Scatter(x=[-0.4*flame_intensity, 0.4*flame_intensity, 1.2*flame_intensity, -1.2*flame_intensity, -0.4*flame_intensity], 
                               y=[1, 1, -2*flame_intensity, -2*flame_intensity, 1], fill="toself", 
                               fillcolor='orange', opacity=0.8, line=dict(color='red'), name="Exhaust Plume"))
fig_flame.update_layout(xaxis=dict(range=[-3, 3], visible=False), yaxis=dict(range=[-4, 3], visible=False), 
                        height=300, margin=dict(l=0, r=0, t=0, b=0), template="plotly_dark", showlegend=False)
st.plotly_chart(fig_flame, use_container_width=True)

# --- PERFORMANCE DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma-DNA (γ)", f"{g_calc:.3f}")
c2.metric("Max Velocity", f"{df['Velocity (m/s)'].max()} m/s")
c3.metric("Peak Acoustic", f"{df['Acoustic (dB)'].max()} dB")
c4.metric("Min Safety Margin", f"{df['Safety Margin (MoS)'].min():.2%}")

st.divider()

# --- INDEPENDENT SENSOR ANALYTICS ---
st.subheader("📈 Independent Sensor Analytics Suite")
r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Chamber Pressure (Ablative Morphing)", template="plotly_dark", yaxis_title="Bar"))
with r2:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Safety Margin (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Global Structural Margin of Safety (MoS)", template="plotly_dark", yaxis_title="Ratio"))

# PDF EXPORT ENGINE
def generate_pdf(data_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story, styles = [], getSampleStyleSheet()
    story.append(Paragraph("V-MAX MASTER TECHNICAL DEFENSE REPORT", styles['Title']))
    story.append(Paragraph("Developer: R. Puneesh kumar", styles['Normal']))
    story.append(Spacer(1, 12))
    table_data = [data_df.columns.tolist()] + data_df.values.tolist()
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0c14b")), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    story.append(t)
    doc.build(story)
    return buffer.getvalue()

st.download_button("📥 Download Final Technical Defense PDF", data=generate_pdf(df), file_name="VMAX_Final_Report.pdf")
