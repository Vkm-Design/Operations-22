
import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Advanced Component Router", layout="wide")

st.title("⚙️ Engineering Process Planner & Routing Engine")
st.write("Fill out the global component details below. The system will cascade these dimensions through all 22 operations.")

#---
# --- Step 1: Global Settings & Documentation ---
st.header("📋 Global Component Specifications")

# Documentation Fields
with st.container():
    doc_col1, doc_col2, doc_col3 = st.columns(3)
    with doc_col1:
        doc_num = st.text_input("Document Number", value="DOC-2026-001")
    with doc_col2:
        part_name = st.text_input("Part Name", value="Main Shaft / Valve Body")
    with doc_col3:
        customer_name = st.text_input("Customer Name", value="Global Machining Corp")

st.markdown("---")

# Dimensional & Feature Fields
dim_col1, dim_col2, dim_col3, dim_col4 = st.columns(4)

with dim_col1:
    finish_dia_1 = st.number_input("Finish Diameter 1 (mm)", min_value=0.0, value=35.0, step=0.1)
    finish_dia_2 = st.number_input("Finish Diameter 2 (mm)", min_value=0.0, value=25.0, step=0.1)
    thickness = st.number_input("Thickness / Length of Part (mm)", min_value=0.0, value=60.0, step=1.0)

with dim_col2:
    # Logic rule for Input Dia 1: Automatically defaults to Finish Dia 1 + Machining Allowance (e.g., +4mm stock)
    # The user can still overwrite this if they want.
    suggested_input_d1 = finish_dia_1 + 4.0
    input_dia_1 = st.number_input("Input Diameter 1 (mm)", min_value=0.0, value=suggested_input_d1, step=1.0, 
                                  help="Automatically estimated based on Finish Dia 1 plus stock allowance.")
    
    # Input Dia 2: Comes as solid stock (0mm internal or full starting stock)
    input_dia_2 = st.number_input("Input Diameter 2 (mm) [Solid/Pre-bore]", min_value=0.0, value=0.0, step=1.0,
                                  help="Generally 0 if starting from a solid bar.")

with dim_col3:
    side_hole_qty = st.selectbox("Side Hole Qty", [1, 2], index=0)
    side_hole_dia_1 = st.number_input("Side Hole Dia 1 (mm)", min_value=0.0, value=10.0, step=0.5)
    side_hole_dia_2 = st.number_input("Side Hole Dia 2 (mm)", min_value=0.0, value=12.0, step=0.5)

with dim_col4:
    tolerance_all = st.number_input("General Tolerance (mm)", min_value=0.000, value=0.025, format="%.3f", step=0.005)
    surface_finish = st.number_input("Surface Finish Requirement (Ra)", min_value=0.0, value=1.6, step=0.4, format="%.1f")

st.markdown("---")

# Global Economic Constants
with st.expander("Costing & Production Volume Settings"):
    econ_col1, econ_col2 = st.columns(2)
    with econ_col1:
        batch_size = st.number_input("Production Batch Size (pcs)", min_value=1, value=500, step=50)
    with econ_col2:
        base_hourly_rate = st.number_input("Base Machine Hourly Rate ($/hr)", min_value=1.0, value=45.0, step=5.0)

#---
# --- Step 2: Automated 22-Operation Engineering Engine ---

routing_data = []

# Loop through all 22 operations sequentially
for op_num in range(1, 23):
    op_name = f"Operation {op_num:02d}"
    
    # Placeholders for the metrics we need to calculate/define per operation
    process_description = "Pending Process Allocation"
    cycle_time = 0.0
    tool_cost_batch = 0.0
    m_rate = base_hourly_rate
    
    # --- WRITE YOUR INDEPENDENT INPUT, LOGIC & OUTPUT RULES HERE ---
    
    if op_num == 1:
        process_description = "Facing & Turning Raw Stock (Dia 1)"
        # LOGIC: Uses Input Diameter 1 and thickness to determine material removal time
        # OUTPUT: Pre-turned outer diameter close to finish sizing
        stock_to_remove = input_dia_1 - finish_dia_1
        cycle_time = (stock_to_remove * 0.5) + (thickness * 0.02)
        tool_cost_batch = 150.0
        
    elif op_num == 2:
        process_description = "Solid Core Drilling (Dia 2)"
        # LOGIC: Uses Finish Diameter 2 because Input Diameter 2 was solid (0mm)
        # OUTPUT: Rough bored ID hole
        if input_dia_2 == 0:
            cycle_time = (finish_dia_2 * 0.1) * (thickness / 10)
        else:
            cycle_time = ((finish_dia_2 - input_dia_2) * 0.05) * (thickness / 10)
        tool_cost_batch = 200.0
        
    elif op_num == 3:
        process_description = "Side Hole Drilling & Deburring"
        # LOGIC: Scaled explicitly by side hole quantities and diameters
        # OUTPUT: Side cross holes matching specifications
        hole_factor = side_hole_qty * (side_hole_dia_1 + side_hole_dia_2)
        cycle_time = hole_factor * 0.15
        tool_cost_batch = 75.0
        
    elif op_num == 4:
        process_description = "Finish Grinding / Boring"
        # LOGIC: Tight tolerance and high surface finish requires extra time factor
        # OUTPUT: Final precision geometry meeting Ra specs
        if surface_finish <= 1.6 or tolerance_all <= 0.02:
            cycle_time = 4.5  # Slower precision pass
            m_rate = base_hourly_rate * 1.3  # Higher tier machine
        else:
            cycle_time = 2.0
        tool_cost_batch = 300.0

    else:
        # Fallback default placeholders for operations 5 to 22
        process_description = f"Operation {op_num:02d} Standard Process Step"
        cycle_time = 1.5
        tool_cost_batch = 50.0

    # --- MATH ENGINE ---
    machining_cost_pc = (cycle_time / 60) * m_rate
    tool_cost_pc = tool_cost_batch / batch_size
    total_op_cpc = machining_cost_pc + tool_cost_pc
    shift_output = (8 * 60) / cycle_time if cycle_time > 0 else 0
    
    # Save step results
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

#---
# --- Step 3: Document Summary Display ---
st.markdown("---")
st.subheader("📄 Manufacturing Routing Card Summary")

# Meta Information Block
meta_col1, meta_col2, meta_col3 = st.columns(3)
with meta_col1:
    st.write(f"**Document No:** {doc_num}")
    st.write(f"**Customer:** {customer_name}")
with meta_col2:
    st.write(f"**Part Name:** {part_name}")
    st.write(f"**Target Batch:** {batch_size} units")
with meta_col3:
    total_time = df_routing["Cycle Time (Min)"].sum()
    total_cpc = df_routing["Total Stage CPC ($)"].sum()
    st.write(f"**Total Estimated Cycle Time:** {total_time:.2f} Mins")
    st.write(f"**Total Process CPC:** ${total_cpc:.2f}")

st.markdown("---")
# Render Interactive Spreadsheet View
st.dataframe(df_routing.set_index("Operation"), use_container_width=True)
