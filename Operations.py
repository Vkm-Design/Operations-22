import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Advanced Component Router", layout="wide")

st.title("⚙️ Engineering Process Planner & Routing Engine")
st.write("Fill out the global component details below. The system will cascade these dimensions through all 22 operations.")

# --- Step 1: Global Settings & Documentation ---
st.header("📋 Global Component Specifications")

# Documentation Fields
doc_col1, doc_col2, doc_col3 = st.columns(3)
with doc_col1:
    doc_num = st.text_input("Document Number", value="DOC-2026-001")
with doc_col2:
    part_name = st.text_input("Part Name", value="Main Shaft / Valve Body")
with doc_col3:
    customer_name = st.text_input("Customer Name", value="Global Machining Corp")

# --- Step 2: Global Material & Hardness Options ---
st.subheader("🪵 Material Selection")
mat_col1, mat_col2, mat_col3 = st.columns(3)
with mat_col1:
    material_type = st.selectbox("Material Grade", ["Aluminium", "Carbon Steel", "Alloy Steel", "Stainless Steel"])
with mat_col2:
    hardness_value = st.text_input("Hardness (e.g., 30 HRC, 220 HB)", value="32 HRC")
with mat_col3:
    batch_size = st.number_input("Production Batch Size (pcs)", min_value=1, value=500, step=50)

# --- Step 3: Horizontal Sizing Matrix (Lines 1 & 2) ---
st.subheader("📐 Diameter & Thickness Parameters")

# Line 1: D1 Parameters
st.markdown("**Line 1: Diameter 1 (D1) Sizing**")
d1_col1, d1_col2, d1_col3, d1_col4, d1_col5 = st.columns(5)
with d1_col1:
    finish_dia_1 = st.number_input("Finish Size D1 (mm)", min_value=0.0, value=35.0, step=0.1)
with d1_col2:
    tolerance_d1 = st.number_input("D1 Tolerance (mm)", min_value=0.000, value=0.025, format="%.3f", step=0.005)
with d1_col3:
    surface_finish_d1 = st.number_input("D1 Surface Finish (Ra)", min_value=0.0, value=1.6, step=0.4, format="%.1f")
with d1_col4:
    suggested_input_d1 = finish_dia_1 + 4.0
    input_dia_1 = st.number_input("Input Size D1 (mm)", min_value=0.0, value=suggested_input_d1, step=1.0)
with d1_col5:
    thickness_d1 = st.number_input("Thickness/Length for D1 (mm)", min_value=0.0, value=40.0, step=1.0)

# Line 2: D2 Parameters
st.markdown("**Line 2: Diameter 2 (D2) Sizing**")
d2_col1, d2_col2, d2_col3, d2_col4, d2_col5 = st.columns(5)
with d2_col1:
    finish_dia_2 = st.number_input("Finish Size D2 (mm)", min_value=0.0, value=25.0, step=0.1)
with d2_col2:
    tolerance_d2 = st.number_input("D2 Tolerance (mm)", min_value=0.000, value=0.025, format="%.3f", step=0.005)
with d2_col3:
    surface_finish_d2 = st.number_input("D2 Surface Finish (Ra)", min_value=0.0, value=1.6, step=0.4, format="%.1f")
with d2_col4:
    input_dia_2 = st.number_input("Input Size D2 (mm) [Solid]", min_value=0.0, value=0.0, step=1.0)
with d2_col5:
    thickness_d2 = st.number_input("Thickness/Length for D2 (mm)", min_value=0.0, value=20.0, step=1.0)

# --- Step 4: Oil Hole Sizing Parameters ---
st.subheader("🛢️ Oil Hole Specifications")

# Row 1: Oil Hole 1 Configurations
st.markdown("**Oil Hole 1 Parameters**")
oh1_col1, oh1_col2, oh1_col3, oh1_col4 = st.columns(4)
with oh1_col1:
    oil_hole_qty_1 = st.number_input("Hole 1 Qty", min_value=0, value=1, step=1)
with oh1_col2:
    oil_hole_dia_1 = st.number_input("Hole 1 Size/Dia (mm)", min_value=0.0, value=10.0, step=0.5)
with oh1_col3:
    oil_hole_finish_1 = st.number_input("Hole 1 Surface Finish (Ra)", min_value=0.0, value=3.2, step=0.4, format="%.1f")
with oh1_col4:
    oil_hole_depth_1 = st.number_input("Hole 1 Depth (mm)", min_value=0.0, value=15.0, step=1.0)

# Row 2: Oil Hole 2 Configurations
st.markdown("**Oil Hole 2 Parameters**")
oh2_col1, oh2_col2, oh2_col3, oh2_col4 = st.columns(4)
with oh2_col1:
    oil_hole_qty_2 = st.number_input("Hole 2 Qty", min_value=0, value=0, step=1)
with oh2_col2:
    oil_hole_dia_2 = st.number_input("Hole 2 Size/Dia (mm)", min_value=0.0, value=12.0, step=0.5)
with oh2_col3:
    oil_hole_finish_2 = st.number_input("Hole 2 Surface Finish (Ra)", min_value=0.0, value=3.2, step=0.4, format="%.1f")
with oh2_col4:
    oil_hole_depth_2 = st.number_input("Hole 2 Depth (mm)", min_value=0.0, value=20.0, step=1.0)

# --- Step 5: Automated 22-Operation Engineering Engine ---
base_hourly_rate = 45.0
routing_data = []

for
