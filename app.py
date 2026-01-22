import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- 1. GLOBAL STYLING ---
st.set_page_config(page_title="V-MAX Aerospace Guru", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #f0c14b !important; font-weight: bold; font-size: 2.2rem; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    [data-testid="stMetric"] { background-color: #1c232d; padding: 20px; border-radius: 12px; border-bottom: 4px solid #f0c14b; }
    h1, h2, h3, h4 { color: #f0c14b !important; }
    div.stButton > button:first-child { background-color: #f0c14b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED PHYSICS ENGINE (SEC-TO-SEC) ---
def run_transient_physics(temp, mach, duration, p_init, w_cu_ratio):
    t_steps = np.arange(0, duration + 1, 1) # Per-second steps
    gamma = 1.21
    
    # Material Logic: W-Cu Erosion Factor
    erosion_base = 0.05 if w_cu_ratio > 75 else 0.15
    erosion_series = erosion_base * (temp / 3000) * (1 + 0.01 * t_steps)
    
    # Performance Decay
    p_decay = p_init * np.exp(-0.005 * t_steps)
    acoustic_load = 10 * np.log10((temp/10)**4) + 120 - (2 * t_steps) # Transient Acoustic Map
    
    # Area Ratio Adjusting for Boundary Layer (2% loss)
    ar = ((1/mach) * ((2/(gamma+1))*(1+((gamma-1)/2)*mach**2))**((gamma+1)/(2*(gamma-1)))) * 0.98
    
    return pd.DataFrame({
        "Time (s)": t_steps,
        "Pressure (Bar)": np.round(p_decay, 2),
        "Acoustic Load (dB)": np.round(acoustic_load, 1),
        "Erosion Rate (mm/s)": np.round(erosion_series, 4)
    }), ar

# --- 3. COMMAND SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/rocket.png", width=70)
    st.title("V-MAX MISSION CONTROL")
    t_goal = st.slider("Chamber Temp (K)", 1500, 3500, 3032)
    m_goal = st.slider("Target Mach", 0.5, 4.0, 1.25)
    p_start = st.slider("Initial Pressure (Bar)", 10, 80, 35)
    w_cu = st.slider("W-Cu Mixer (% Tungsten)", 50, 95, 75)
    burn_time = st.number_input("Burn Duration (s)", 10, 300, 20)

# Calculate Data
df_results, ar_eff = run_transient_physics(t_goal, m_goal, burn_time, p_start, w_cu)

# --- 4. DASHBOARD UI ---
st.title("🚀 HGG-JDD V-MAX Master Guru")
st.markdown("#### High-Fidelity Aerospace Digital Twin: Transient Multi-Physics")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Eff. Area Ratio", f"{ar_eff:.3f}")
m2.metric("O/F Ratio (DNA)", f"{(1.0 + (t_goal-1500)/400):.2f}")
m3.metric("Peak Acoustic", f"{df_results['Acoustic Load (dB)'].max()} dB")
m4.metric("Burn Status", "Transient Active")

st.divider()

# Sec-to-Sec Visuals
c1, c2 = st.columns(2)
with c1:
    fig_p = go.Figure(data=go.Scatter(x=df_results['Time (s)'], y=df_results['Pressure (Bar)'], mode='lines+markers', line=dict(color='#f0c14b')))
    fig_p.update_layout(title="Sec-to-Sec Pressure Decay", template="plotly_dark", xaxis_title="Time (s)", yaxis_title="Bar")
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    fig_a = go.Figure(data=go.Scatter(x=df_results['Time (s)'], y=df_results['Acoustic Load (dB)'], mode='lines', fill='tozeroy', line=dict(color='#00d4ff')))
    fig_a.update_layout(title="Sec-to-Sec Acoustic Fatigue Profile", template="plotly_dark", xaxis_title="Time (s)", yaxis_title="dB")
    st.plotly_chart(fig_a, use_container_width=True)

# --- 5. PDF REPORT GENERATOR ---
def generate_pdf(data_df, temp, mach, ar):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title & Header
    story.append(Paragraph("ISRO-GRADE TECHNICAL REPORT: HGG-JDD V-MAX", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Mission Parameters:</b> Temp: {temp}K | Mach: {mach} | Eff. AR: {ar:.3f}", styles['Normal']))
    story.append(Spacer(1, 24))

    # Data Table
    table_data = [data_df.columns.tolist()] + data_df.values.tolist()
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0c14b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    
    doc.build(story)
    return buffer.getvalue()

st.divider()
pdf_data = generate_pdf(df_results, t_goal, m_goal, ar_eff)
st.download_button(
    label="📥 Download Professional Engineering PDF Report",
    data=pdf_data,
    file_name="VMAX_ISRO_Technical_Report.pdf",
    mime="application/pdf"
)
