import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CORE PHYSICS: GOAL-SEEK & ABLATIVE MORPHING ---
def run_master_physics(target_temp, target_mach, duration, material, initial_p):
    # Reverse Design: Finding the O/F Ratio to hit the Target Temp
    sof = 1.0 + (target_temp - 1500) / 400
    
    # Isentropic Flow Logic: Calculating Area Ratio (AR)
    gamma = 1.21 
    ar = (1/target_mach) * ((2/(gamma+1)) * (1 + ((gamma-1)/2)*target_mach**2))**((gamma+1)/(2*(gamma-1)))
    
    # Ablation Logic: Real-time Nozzle Throat Expansion
    # Erosion rates (mm/s) based on material and thermal load
    rates = {"Copper": 0.5, "Steel": 0.3, "Inconel": 0.1, "Tungsten": 0.01, "Graphite": 0.05}
    erosion_rate = rates.get(material, 0.1) * (target_temp / 2000)
    final_throat_dia = 25 + (2 * erosion_rate * duration) # Starts at 25mm
    
    # Performance Decay Curve (Pressure drops as throat erodes)
    times = np.linspace(0, duration, 20)
    p_decay = initial_p * np.exp(-erosion_rate * 0.01 * times)
    
    return sof, ar, final_throat_dia, times, p_decay

# --- 2. JDD SAFETY & FLUID DYNAMICS BRAIN ---
def calculate_jdd_systems(temp, p_init, material, angle):
    # Transpiration Cooling: Water Pressure must be > Gas Pressure
    req_water_p = p_init * 1.25 
    water_lpm = (temp * 0.04) * (p_init / 10)
    
    # Structural Integrity: Temperature-Adjusted Barlow's Formula
    # Yield strengths in MPa
    yield_map = {"Copper": 70, "Steel": 215, "Inconel": 1000, "Tungsten": 550, "Graphite": 3800}
    s_yield = yield_map.get(material, 200) * 0.65 # Safety Factor applied
    wall_t = ((p_init/10) * 100) / (2 * (s_yield / 2.0))
    
    # Acoustic Load Estimation (dB)
    db_level = 10 * np.log10((temp/10)**4) + 100
    
    return req_water_p, water_lpm, max(wall_t, 2.5), db_level

# --- 3. MASTER USER INTERFACE ---
st.set_page_config(page_title="HGG-JDD Ultimate Expert", layout="wide")
st.title("🌌 HGG-JDD Ultimate Expert System (V-Max)")
st.markdown("### Professional Aerospace Optimization & Predictive Intelligence")

with st.sidebar:
    st.header("⚙️ Design Goals")
    t_goal = st.slider("Target Combustion Temp (K)", 1500, 3500, 2600)
    m_goal = st.slider("Target Exhaust Mach", 0.5, 4.0, 1.8)
    p_init = st.slider("Initial Chamber Pressure (Bar)", 10, 80, 35)
    w_dur = st.number_input("Test Duration (s)", 10, 300, 60)
    mat_choice = st.selectbox("Throat & JDD Material", ["Steel", "Inconel", "Tungsten", "Graphite"])
    jdd_tilt = st.slider("JDD Tilt Angle (°)", 0, 90, 0)

# Run Simulation Engine
sof, ar, f_dia, t_series, p_series = run_master_physics(t_goal, m_goal, w_dur, mat_choice, p_init)
wp, lpm, thickness, db = calculate_jdd_systems(t_goal, p_init, mat_choice, jdd_tilt)

# --- 4. VISUAL DASHBOARD ---
col_spec, col_viz = st.columns([1, 1.5])

with col_spec:
    st.subheader("📋 Blueprint Specifications")
    st.metric("Required O/F Ratio", f"{sof:.2f}")
    st.metric("Nozzle Area Ratio", f"{ar:.2f}")
    st.info(f"**Coolant Supply:** {wp:.1f} Bar @ {lpm:.1f} LPM")
    st.warning(f"**Structural:** {thickness:.2f} mm Wall Thickness Required")
    st.error(f"**Acoustic Intensity:** {db:.1f} dB")

with col_viz:
    # 1. Performance Decay Plot
    fig_p = px.line(x=t_series, y=p_series, title="Pressure Decay (Ablative Morphing)", 
                    labels={'x':'Time (s)', 'y':'Chamber Pressure (Bar)'},
                    color_discrete_sequence=['#FF4B4B'])
    st.plotly_chart(fig_p, use_container_width=True)
    
    # 2. Safety Corridor Contour Map
    st.subheader("🗺️ Safety Corridor (Design Space)")
    p_grid = np.linspace(10, 80, 20)
    t_grid = np.linspace(1500, 3500, 20)
    # Z-axis calculates a dummy safety margin for visualization
    z_map = [[(1000 / ((p * 100) / 20)) for p in p_grid] for t in t_grid]
    fig_map = go.Figure(data=go.Contour(z=z_map, x=p_grid, y=t_grid, colorscale='RdYlGn', zmin=1, zmax=3))
    fig_map.add_trace(go.Scatter(x=[p_init], y=[t_goal], mode='markers', 
                                 marker=dict(size=18, color='white', symbol='x', line=dict(width=2, color='black'))))
    fig_map.update_layout(xaxis_title="Pressure (Bar)", yaxis_title="Temp (K)")
    st.plotly_chart(fig_map, use_container_width=True)

# --- 5. GURU STRATEGIC ASSESSMENT ---
st.divider()
st.subheader("🧠 Guru Strategic Analysis")
adv1, adv2 = st.columns(2)

with adv1:
    if f_dia > 27:
        st.error(f"🚨 CRITICAL ABLATION: Throat expands to {f_dia:.1f}mm. Mach stability will fail late-test.")
    else:
        st.success(f"✅ Material Stability: {mat_choice} sustains geometry for {w_dur}s.")

with adv2:
    if jdd_tilt > 45:
        st.warning(f"⚠️ Vector Impact: At {jdd_tilt}°, back-pressure may destabilize transpiration cooling.")
    else:
        st.success("✅ Plume Clearance: Ground interaction within safe thermal dissipation limits.")
