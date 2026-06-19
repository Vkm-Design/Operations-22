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

for op_num in range(1, 23):
    op_name = f"Operation {op_num:02d}"
    process_description = "Standard Process Step"
    cycle_time = 1.5
    tool_cost_batch = 50.0
    m_rate = base_hourly_rate
    
    # --- EDIT INDIVIDUAL OPERATION LOGIC BELOW ---
    if op_num == 1:
        process_description = f"Rough Turn Outer Dia 1 from Ø{input_dia_1} to Ø{finish_dia_1}"
        stock_to_remove = input_dia_1 - finish_dia_1
        cycle_time = (stock_to_remove * 0.4) + (thickness_d1 * 0.02)
        tool_cost_batch = 120.0
        
    elif op_num == 2:
        process_description = f"Bore Internal Dia 2 (Depth: {thickness_d2}mm)"
        if input_dia_2 == 0:
            cycle_time = (finish_dia_2 * 0.1) * (thickness_d2 / 10)
        else:
            cycle_time = ((finish_dia_2 - input_dia_2) * 0.05) * (thickness_d2 / 10)
        tool_cost_batch = 180.0
        
    elif op_num == 3:
        process_description = f"Drill {oil_hole_qty_1} Oil Hole(s) Ø{oil_hole_dia_1} to Depth {oil_hole_depth_1}mm"
        if oil_hole_qty_1 > 0:
            cycle_time = (oil_hole_qty_1 * oil_hole_depth_1 * 0.05)
        else:
            cycle_time = 0.0
            process_description = "Oil Hole 1 Stage Skipped"
        tool_cost_batch = 60.0

    # Math calculations
    machining_cost_pc = (cycle_time / 60) * m_rate
    tool_cost_pc = tool_cost_batch / batch_size
    total_op_cpc = machining_cost_pc + tool_cost_pc
    shift_output = (8 * 60) / cycle_time if cycle_time > 0 else 0
    
    routing_data.append({
        "Operation": op_name,
        "Process Description": process_description,
        "Cycle Time (Min)": round(cycle_time, 2),
        "Machine Cost/Pc ($)": round(machining_cost_pc, 2),
        "Tool Cost/Pc ($)": round(tool_cost_pc, 2),
        "Total Stage CPC ($)": round(total_op_cpc, 2),
        "Shift Yield (pcs)": int(shift_output)
    })

df_routing = pd.DataFrame(routing_data)

# --- Step 6: Document Summary Display ---
st.subheader("📄 Manufacturing Routing Card Summary")

meta_col1, meta_col2, meta_col3 = st.columns(3)
with meta_col1:
    st.write(f"**Document No:** {doc_num}")
    st.write(f"**Customer:** {customer_name}")
with meta_col2:
    st.write(f"**Part Name:** {part_name}")
    st.write(f"**Material & Hardness:** {material_type} ({hardness_value})")
with meta_col3:
    total_time = df_routing["Cycle Time (Min)"].sum()
    total_cpc = df_routing["Total Stage CPC ($)"].sum()
    st.write(f"**Total Estimated Cycle Time:** {total_time:.2f} Mins")
    st.write(f"**Total Process CPC:** ${total_cpc:.2f}")

st.dataframe(df_routing.set_index("Operation"), use_container_width=True)
