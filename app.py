import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- 1. GLOBAL STYLING (AEROSPACE DARK THEME) ---
st.set_page_config(page_title="V-MAX Super-Guru", layout="wide", page_icon="🚀")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #f0c14b !important; font-weight: bold; font-size: 2.2rem; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    [data-testid="stMetric"] { background-color: #1c232d; padding: 20px; border-radius: 12px; border-bottom: 4px solid #f0c14b; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED TRANSIENT ENGINE (MOTOR & JDD PHYSICS) ---
def run_firing_sim(temp, mach, duration, p_init, w_cu_ratio):
    t_steps = np.arange(0, duration + 1, 1)
    gamma = 1.21
    
    # Paraffin Regression & Motor Firing Logic
    erosion_factor = 0.04 if w_cu_ratio > 80 else 0.12
    p_decay = p_init * np.exp(-0.008 * t_steps)
    acoustic_series = (10 * np.log10((temp/10)**4) + 120) - (0.5 * t_steps)
    
    # Effective Flow Area (Viscous Boundary Layer) 
    ar_geom = (1/mach) * ((2/(gamma+1))*(1+((gamma-1)/2)*mach**2))**((gamma+1)/(2*(gamma-1)))
    ar_eff = ar_geom * 0.985 
    
    # JDD Impingement Heat Flux (Stagnation Point) 
    heat_flux = (temp / 100) * np.sqrt(p_decay / 35)
    
    return pd.DataFrame({
        "Sec": t_steps,
        "Chamber Pressure (Bar)": np.round(p_decay, 2),
        "Acoustic Load (dB)": np.round(acoustic_series, 1),
        "Plate Heat Flux (MW/m2)": np.round(heat_flux, 2)
    }), ar_eff

# --- 3. MISSION CONTROL SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/rocket.png", width=70)
    st.title("V-MAX MISSION CONTROL")
    t_goal = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    m_goal = st.slider("Target Mach", 0.5, 4.0, 1.25)
    p_start = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    w_cu = st.slider("W-Cu Mixer (% W)", 50, 95, 75)
    burn_time = st.number_input("Burn Duration (s)", 5, 60, 20)

df_results, ar_eff = run_firing_sim(t_goal, m_goal, burn_time, p_start, w_cu)

# --- 4. DASHBOARD & LIVE FIRING VISUALIZATION ---
st.title("🚀 HGG-JDD V-MAX Master Guru")
st.markdown("#### Aerospace Digital Twin: Live Motor Firing & JDD Impingement Simulation [cite: 5, 14]")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Eff. Area Ratio", f"{ar_eff:.3f}")
m2.metric("O/F Ratio (DNA)", f"{(1.0 + (t_goal-1500)/400):.2f}")
m3.metric("Peak Heat Flux", f"{df_results['Plate Heat Flux (MW/m2)'].max()} MW/m²")
m4.metric("Hardware", f"W-Cu Mixer")

st.divider()

# LIVE FIRING PLUME VISUALIZATION
st.subheader("🔥 Live Motor Firing & JDD Plume Impingement")
col_vis, col_data = st.columns([2, 1])

with col_vis:
    # 2D Heatmap of Plume hitting JDD Plate
    grid_size = 30
    x = np.linspace(-15, 15, grid_size)
    y = np.linspace(-15, 15, grid_size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    # Stagnation Point Physics: Intensity drops radially from center of JDD
    Z = (t_goal / 10) * np.exp(-0.2 * R) * (df_results['Chamber Pressure (Bar)'].iloc[-1] / p_start)
    
    fig_plume = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Hot')])
    fig_plume.update_layout(title="JDD Plate Stagnation Heat Map", template="plotly_dark",
                          scene=dict(xaxis_title="X (cm)", yaxis_title="Y (cm)", zaxis_title="Temp (K)"))
    st.plotly_chart(fig_plume, use_container_width=True)

with col_data:
    st.write("Sec-to-Sec Firing Data")
    st.dataframe(df_results[['Sec', 'Chamber Pressure (Bar)', 'Plate Heat Flux (MW/m2)']], height=400)

# --- 5. REPORT EXPORT ---
def generate_pdf(df, temp, mach, ar):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story, styles = [], getSampleStyleSheet()
    story.append(Paragraph("V-MAX AEROSPACE FIRING REPORT", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Mission:</b> {temp}K | Mach {mach} | Area Ratio {ar:.3f}", styles['Normal']))
    
    table_data = [df.columns.tolist()] + df.values.tolist()
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0c14b")), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(t)
    doc.build(story)
    return buffer.getvalue()

st.divider()
st.download_button("📥 Download Sec-to-Sec Firing PDF", data=generate_pdf(df_results, t_goal, m_goal, ar_eff), file_name="VMAX_Firing_Report.pdf")
