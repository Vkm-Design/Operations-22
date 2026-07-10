import streamlit as st
import pandas as pd
import math
import io

# --- Configuration & Master Data ---
st.set_page_config(layout="wide", page_title="Con Rod Process Planner", page_icon="⚙️")

OPERATION_NAMES = [
    "Inward Inspection Of Forging",
    "Rough Thickness Grinding",
    "Combined Operations- VMC",
    "Big End Chamfering 2nd Side",
    "Heat treatment, (Case carburizing, Hardening & temper)",
    "Shot blasting",
    "Induction softening",
    "Finish Thickness Grinding",
    "Hard Boring B/E & S/E",
    "Oil Hole Drilling & Chamfering",
    "Oil Hole Deburing",
    "Small End Chamfering",
    "B/E Honning",
    "S/E Honning",
    "Crack Inspection",
    "Demagnetising",
    "High Pressure Cleaning",
    "Visual Inspection-100%",
    "100% Inspection (CD, Bend & Twist )",
    "Laser Marking",
    "Final Inspection",
    "Oiling & Packing"
]

MACHINE_COST_DEFAULTS = {
    "Manual": 0,
    "Manual with Gauge": 0,
    "SDG (Ø600)- For CR Thickness Grinding": 36,
    "Makino": 60,
    "Sansera Horizontal Machine": 45,
    "SQF": 80,
    "Shot Blasting M/c": 18,
    "IH M/c": 22,
    "SFB 02- For CR Fine Boring with Index table & NT": 55,
    "SHD 03/ SID- For CR Oil Hole Drilling": 28,
    "Deburring Station": 10,
    "Drilling Machine": 15,
    "SVH- For CR Vertical Honing/Big End Honing": 35,
    "MPI": 12,
    "Demagnetiser": 5,
    "CLEANING 01- Cleantech": 20,
    "Laser Marking M/c": 25,
}

# --- Application Header Banner ---
st.title("⚙️ Con Rod Process Planner & Routing Engine")
st.caption("Connecting Rod — 22 Operations | Automated Cycle Time, Tool Wear & Cost Calculation")

# --- Layout Panels ---
sidebar, main_content = st.columns([1, 3])

with sidebar:
    st.header("📋 Document Metadata")
    doc_num = st.text_input("Document Number", value="DOC-2026-001")
    part_name = st.text_input("Part Name", value="Con Rod — SCr420HV")
    customer = st.text_input("Customer Name", value="Global Corp")
    
    st.header("🪵 Material & Parameters")
    mat_grade = st.selectbox("Material Grade", ["Steel (up to 30 HRC)", "Steel (30–40 HRC)"])
    hrc_corr = {"rpm": 0.90, "feed": 0.95} if "30–40" in mat_grade else {"rpm": 1.0, "feed": 1.0}
    
    batch_size = st.number_input("Batch Size (pcs)", min_value=1, value=500)
    base_hourly_rate = st.number_input("Base Hourly Rate (INR/hr)", min_value=1, value=500)
    efficiency = st.number_input("Shift Efficiency (%)", min_value=1, max_value=100, value=90) / 100.0

    st.header("📐 Component Sizing")
    finish_dia1 = st.number_input("Big End Diameter (mm)", value=38.0)
    thickness_d1 = st.number_input("Big End Thickness (mm)", value=16.0)
    finish_dia2 = st.number_input("Small End Diameter (mm)", value=14.0)
    thickness_d2 = st.number_input("Small End Thickness (mm)", value=16.0)
    oil_hole_depth = st.number_input("Oil Hole Depth (mm)", value=3.0)

# --- Place this function right above the loop ---
def calculate_op3_vmc_cycle(finish_dia1, thickness_d1, finish_dia2, thickness_d2, hrc_corr):
    """
    Replicates the exact mathematical behavior of calcOp3CycleTime from your script.
    """
    MAKINO_TOOL_CHANGE = 3.3
    MAKINO_POSITION = 1.2
    
    # --- Big End (Bore) Sizing & Time Logic ---
    be_step1_d = round(finish_dia1 - 0.66, 2)
    be_step2_d = round(finish_dia1 - 0.36, 2)
    
    vc_boring = 120 * hrc_corr["rpm"]
    feed_fn = 0.12 * hrc_corr["feed"]
    
    rpm_be = (vc_boring * 1000) / (math.pi * finish_dia1) if finish_dia1 > 0 else 1000
    feed_rate_be = rpm_be * feed_fn
    
    approach_allowance = 4.0 
    be_cut_time = ((thickness_d1 + approach_allowance) / feed_rate_be) * 60 if feed_rate_be > 0 else 15
    
    # --- Small End Sizing & Selection Logic ---
    if finish_dia2 <= 20:
        se_drill_d = round(finish_dia2 - 0.36, 2)
        vc_drill = 60 * hrc_corr["rpm"]
        rpm_se = (vc_drill * 1000) / (math.pi * se_drill_d) if se_drill_d > 0 else 1000
        feed_rate_se = 255 * hrc_corr["feed"] 
        se_cut_time = ((thickness_d2 + approach_allowance) / feed_rate_se) * 60 if feed_rate_se > 0 else 10
    else:
        rpm_se = (100 * 1000) / (math.pi * finish_dia2)
        feed_rate_se = rpm_se * 0.10
        se_cut_time = ((thickness_d2 + approach_allowance) / feed_rate_se) * 60

    total_machining_seconds = be_cut_time + se_cut_time + (MAKINO_TOOL_CHANGE * 2) + MAKINO_POSITION
    return max(25.0, round(total_machining_seconds, 1))


# --- Process Smart Engine Initial Calculation Mapping ---
calculated_op3_time = max(25.0, round((finish_dia1 * 0.4) + (finish_dia2 * 0.5) + (thickness_d1 * 0.3), 1))

calculated_rows = []
total_cycle_mins = 0.0

for idx, name in enumerate(OPERATION_NAMES, 1):
    machine = "Manual"
    parts_loaded = 1
    op_time = 60
    lu_time = 5
    tool_cost = 1200
    tool_life = 250
    unit = "Parts"
    regrinds = 2
    regrind_cost = 150
    is_manual = False

    # Route operation-specific parameters
    if idx == 1:
        machine, op_time, lu_time, tool_cost, is_manual = "Manual", 0, 0, 0, True
    elif idx in [2, 8]:
        machine, parts_loaded, op_time, lu_time, tool_cost, tool_life = "SDG (Ø600)- For CR Thickness Grinding", 2, 12, 0, 40000, 150000
    elif idx == 3:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "Makino", calculated_op3_time, 0, 6500, 120, "Min"
    elif idx == 4:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "Sansera Horizontal Machine", 48, 5, 800, 200, "Min"
    elif idx in [5, 6, 7]:
        machine = "SQF" if idx==5 else ("Shot Blasting M/c" if idx==6 else "IH M/c")
        op_time, lu_time, tool_cost, is_manual = 0, 0, 0, True
    elif idx == 9:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "SFB 02- For CR Fine Boring with Index table & NT", 15, 0, 3500, 45, "Mtr"
    elif idx == 10:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "SHD 03/ SID- For CR Oil Hole Drilling", 18, 5, 2400, 35, "Mtr"
    elif idx == 11:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "Deburring Station", 10, 0, 0, 1000, "Min"
    elif idx == 12:
        machine, op_time, lu_time, tool_cost, tool_life, unit = "Drilling Machine", 6, 6, 350, 180, "Min"
    elif idx in [13, 14]:
        machine, parts_loaded, op_time, tool_cost, tool_life = "SVH- For CR Vertical Honing/Big End Honing", 6, 64, 21600 if idx==13 else 180000, 40000 if idx==13 else 200000
    elif idx in [15, 16, 17, 18, 19, 20, 21]:
        machine = "MPI" if idx==15 else ("Demagnetiser" if idx==16 else ("CLEANING 01- Cleantech" if idx==17 else ("Laser Marking M/c" if idx==20 else "Manual")))
        op_time, lu_time, tool_cost, unit = (10 if idx in [15,16,18] else (8 if idx==17 else (15 if idx==19 else 6))), 0, 0, "Min"
    elif idx == 22:
        machine, op_time, lu_time, tool_cost, is_manual = "Manual", 0, 0, 0, True

    mc_lakh = MACHINE_COST_DEFAULTS.get(machine, 0)

    # Core Calculations
    if is_manual or op_time == 0:
        cycle_min = 0.0
        parts_per_hr = 0.0
        tool_cost_pc = 0.0
    else:
        total_sec = (op_time / parts_loaded) + lu_time
        cycle_min = total_sec / 60.0
        parts_per_hr = (60.0 / cycle_min) * efficiency if cycle_min > 0 else 0
        
        total_life = tool_life * (1 + regrinds)
        if total_life > 0 and tool_cost > 0:
            tool_cost_pc = (tool_cost + (regrinds * regrind_cost)) / total_life
        else:
            tool_cost_pc = 0.0
            
    if idx == 11:
        tool_cost_pc = 0.30  # Deburring specific override

    total_cycle_mins += cycle_min

    calculated_rows.append({
        "Op #": f"Op {idx:02d}",
        "Operation Name": name,
        "Machine Type": machine,
        "M/c Cost (Lakh)": mc_lakh,
        "Loaded": parts_loaded if not is_manual else 0,
        "Mach (s)": op_time if not is_manual else 0,
        "L/U (s)": lu_time if not is_manual else 0,
        "Cycle (m)": round(cycle_min, 2),
        "Pcs/Hr": round(parts_per_hr, 1),
        "Tool Cost (₹)": tool_cost,
        "Life": tool_life,
        "Unit": unit,
        "Cost/Pc (₹)": round(tool_cost_pc, 2)
    })

df_routing = pd.DataFrame(calculated_rows)
shift_capacity = (480.0 / total_cycle_mins) * efficiency if total_cycle_mins > 0 else 0

# --- Render Main Displays ---
with main_content:
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Total Cycle Time", f"{total_cycle_mins:.2f} Mins")
    kpi2.metric("Avg Shift Capacity", f"{int(shift_capacity)} Pcs", delta_color="normal")
    
    st.subheader("📄 Interactive Live Process Routing Sheet")
    st.dataframe(df_routing, use_container_width=True, hide_index=True)
    
    # Export Setup
    csv_buffer = io.StringIO()
    csv_buffer.write(f"Doc Number,{doc_num}\nPart Name,{part_name}\nCustomer Name,{customer}\n\n")
    df_routing.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="📥 Download Routing Card (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"Routing_Card_{doc_num}.csv",
        mime="text/csv"
    )

    # Graphical Charts Rendering
    st.subheader("⏱️ Process Visual Insights")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.write("**Cycle Time per Operation (Minutes)**")
        df_active_cycle = df_routing[df_routing["Cycle (m)"] > 0]
        st.bar_chart(data=df_active_cycle, x="Op #", y="Cycle (m)", color="#2563eb")
        
    with chart_col2:
        st.write("**Stage Tooling Consumable Cost (₹/pc)**")
        df_active_cost = df_routing[df_routing["Cost/Pc (₹)"] > 0]
        st.bar_chart(data=df_active_cost, x="Op #", y="Cost/Pc (₹)", color="#0d9488")
