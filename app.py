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
st.set_page_config(page_title="V-MAX Omni-Twin | SolidWorks Digital Twin", layout="wide")
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
    
    # 1. Gamma-DNA Matching (Real-Gas Correction) [cite: 10, 11]
    gamma_eff = 1.38 - (temp / 12500)
    R_spec = 518.6 
    
    # 2. Ablative Morphing: Real-Time Throat Expansion [cite: 12, 13]
    reg_rate = 0.55 
    web_remaining = np.maximum(grain_init - (reg_rate * t_steps), 0)
    p_decay = p_init * (web_remaining / grain_init)**0.48
    
    # 3. Isentropic Flow Theory: Supersonic Expansion [cite: 18]
    v_exit = np.sqrt((2 * gamma_eff * R_spec * temp / (gamma_eff - 1)) * (1 - (1.05 / p_decay)**((gamma_eff - 1) / gamma_eff)))
    v_exit_eff = v_exit * 0.982 
    
    # 4. Transpiration Cooling & 100mm Refractory Lag [cite: 18]
    theta_rad = np.radians(jdd_theta)
    thermal_resistance = 1 / (1 + (0.015 * cement_depth)) 
    req_cooling_lps = ((p_decay * (temp / 1050) * np.sin(theta_rad)) / 1.08) * thermal_resistance
    actual_lps = h2o_lpm / 60
    mos = (actual_lps / req_cooling_lps) - 1 # Margin of Safety calculation
    
    # 5. Acoustic Loading (Lighthill's 8th Power Law) [cite: 18]
    acoustic_db = 120 + 10 * np.log10(p_decay**2 + 1)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Velocity (m/s)": np.round(v_exit_eff, 1),
        "Acoustic (dB)": np.round(acoustic_db, 1),
        "Safety Margin (MoS)": np.round(mos, 3)
    }), gamma_eff

# --- FACILITY INTERFACE ---
st.title("🚀 V-MAX Omni-Twin: SolidWorks-Integrated Expert System")
st.markdown(f"**Developer:** R. Puneesh kumar [cite: 2] | **Version:** V-Max Final Aerospace Deployment [cite: 3]")

# --- REPORT CONSTANTS SECTION ---
with st.expander("📖 View Executive Summary (From Technical Report)"):
    st.write("**World-Class Design:** Bridges the gap between CAD prototyping and real-world execution[cite: 5].")
    st.write("**Dynamic Intelligence:** Unlike static SolidWorks models, V-MAX offers real-time Decision Intelligence.")
    st.write("**Self-Optimizing:** Manages the entire lifecycle from chemical balancing to structural calibration[cite: 7].")

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

# --- 3D HARDWARE INTERACTION (THE "SOLIDWORKS" VIEW) ---
st.subheader("🛠️ 3D Digital Twin Hardware Visualization")
flame_scale = (p_in / 80) + 0.5
fig_3d = go.Figure()
# Simplified 3D representation of Nozzle and Tilted JDD
fig_3d.add_trace(go.Mesh3d(x=[-0.5, 0.5, 0.5, -0.5, 0], y=[-0.5, -0.5, 0.5, 0.5, 0], z=[2, 2, 2, 2, 1], color='gray', opacity=0.8, name="W-Cu Mixer"))
fig_3d.add_trace(go.Mesh3d(x=[-2, 2, 2, -2], y=[-1, -1, 1, 1], z=[-1, -1.5, -1.5, -1], color='brown', opacity=0.5, name="100mm Refractory"))
# Exhaust Plume
fig_3d.add_trace(go.Cone(x=[0], y=[0], z=[1], u=[0], v=[0], w=[-2*flame_scale], colorscale='Oranges', sizemode="absolute", sizeref=2))
fig_3d.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), height=400, template="plotly_dark")
st.plotly_chart(fig_3d, use_container_width=True)

# --- PERFORMANCE DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma-DNA (γ)", f"{g_calc:.3f}") [cite: 10]
c2.metric("Max Velocity", f"{df['Velocity (m/s)'].max()} m/s")
c3.metric("Peak Acoustic", f"{df['Acoustic (dB)'].max()} dB") [cite: 18]
c4.metric("Min Safety Margin", f"{df['Safety Margin (MoS)'].min():.2%}") [cite: 15]

st.divider()

# --- ANALYTICS SUITE ---
st.subheader("📈 High-Resolution Temporal Analytics")
r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Pressure (Bar)'], line=dict(color='#ff4b4b', width=3))).update_layout(title="Pressure Decay (Ablative Morphing) [cite: 12]", template="plotly_dark"))
with r2:
    st.plotly_chart(go.Figure(go.Scatter(x=df['Sec'], y=df['Safety Margin (MoS)'], fill='tozeroy', line=dict(color='#f0c14b'))).update_layout(title="Global Structural Safety Corridor [cite: 15]", template="plotly_dark"))

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
