import streamlit as st
import pandas as pd
import json
import os
from datetime import date

st.set_page_config(page_title="Con Rod Process Planner", layout="wide", page_icon="⚙️")

# ── Load master data from JSON files ────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_operations():
    with open(os.path.join(BASE_DIR, "operations.json")) as f:
        return json.load(f)

@st.cache_data
def load_machines():
    with open(os.path.join(BASE_DIR, "machines.json")) as f:
        return json.load(f)

ops_master   = load_operations()
machines_raw = load_machines()
machine_names = [m["name"] for m in machines_raw]
machine_rate  = {m["name"]: m["hourly_rate"] for m in machines_raw}

# ── Category colour badges ───────────────────────────────────────────────────
CAT_COLOUR = {
    "inspection": "🔵",
    "grinding":   "🟠",
    "machining":  "🟣",
    "heat":       "🔴",
    "surface":    "🟡",
    "boring":     "🟢",
    "drilling":   "🟤",
    "deburring":  "⚪",
    "honing":     "🟢",
    "marking":    "🔷",
    "packing":    "🟩",
}

# ── Sidebar: global component specs ─────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x50/1a1a2e/ffffff?text=ConRod+Planner", use_container_width=True)
    st.markdown("### 📋 Component Details")

    doc_num       = st.text_input("Document No.",   value="DOC-2026-001")
    part_name     = st.text_input("Part Name",       value="Connecting Rod")
    customer_name = st.text_input("Customer",        value="")
    rev_no        = st.text_input("Revision No.",    value="A")
    doc_date      = st.date_input("Date",            value=date.today())

    st.markdown("---")
    st.markdown("### 📐 Global Dimensions")
    finish_dia_be = st.number_input("Big End Bore Ø finish (mm)",   min_value=0.0, value=52.0, step=0.1)
    finish_dia_se = st.number_input("Small End Bore Ø finish (mm)", min_value=0.0, value=22.0, step=0.1)
    thickness     = st.number_input("C/R Thickness (mm)",           min_value=0.0, value=28.0, step=0.1)
    length        = st.number_input("C/R Length (mm)",              min_value=0.0, value=140.0, step=1.0)
    tolerance     = st.number_input("General Tolerance (mm)",       min_value=0.000, value=0.025, format="%.3f", step=0.005)
    surface_ra    = st.number_input("Surface Finish Ra",            min_value=0.0, value=1.6, step=0.4, format="%.1f")

    st.markdown("---")
    st.markdown("### 💰 Costing")
    batch_size    = st.number_input("Batch Size (pcs)", min_value=1, value=500, step=50)

# ── Page header ──────────────────────────────────────────────────────────────
st.title("⚙️ Con Rod — Engineering Process Planner")
st.caption(f"Document: **{doc_num}** | Part: **{part_name}** | Customer: **{customer_name}** | Rev: {rev_no} | Date: {doc_date}")
st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_route, tab_summary, tab_admin = st.tabs(["🔩 Routing Card", "📊 Summary & Cost", "⚙️ Admin — Edit Masters"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1: ROUTING CARD
# ════════════════════════════════════════════════════════════════════════════
with tab_route:
    st.subheader("Operation-by-operation routing")
    st.info("Each operation inherits global dimensions. Override cycle time or machine per operation as needed.")

    routing_rows = []

    for op in ops_master:
        op_num  = op["op_num"]
        op_name = op["name"]
        cat     = op.get("category", "")
        badge   = CAT_COLOUR.get(cat, "⚫")
        default_machine = op["default_machine"]
        default_ct      = op["cycle_time_min"]
        default_tc      = op["tool_cost_batch"]

        with st.expander(f"{badge}  Op {op_num:02d} — {op_name}   *(default: {default_machine})*"):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                # Machine dropdown — default pre-selected, user can change
                if default_machine in machine_names:
                    default_idx = machine_names.index(default_machine)
                else:
                    default_idx = 0
                machine = st.selectbox(
                    "Machine / Workstation",
                    options=machine_names,
                    index=default_idx,
                    key=f"machine_{op_num}"
                )

            with col2:
                cycle_time = st.number_input(
                    "Cycle Time (min)",
                    min_value=0.0,
                    value=float(default_ct),
                    step=0.5,
                    key=f"ct_{op_num}"
                )

            with col3:
                tool_cost = st.number_input(
                    "Tool Cost / Batch (₹)",
                    min_value=0.0,
                    value=float(default_tc),
                    step=10.0,
                    key=f"tc_{op_num}"
                )

            # Remarks field
            remarks = st.text_input("Remarks / Notes", value="", key=f"rem_{op_num}", placeholder="Optional notes for this operation...")

            # Derived calculations
            rate          = machine_rate.get(machine, 45)
            mach_cost_pc  = round((cycle_time / 60) * rate, 4)
            tool_cost_pc  = round(tool_cost / batch_size, 4) if batch_size > 0 else 0
            total_cpc     = round(mach_cost_pc + tool_cost_pc, 4)
            shift_yield   = int((8 * 60) / cycle_time) if cycle_time > 0 else 0

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Machine Rate", f"₹{rate}/hr")
            m2.metric("Mach. Cost/pc", f"₹{mach_cost_pc:.3f}")
            m3.metric("Tool Cost/pc",  f"₹{tool_cost_pc:.3f}")
            m4.metric("Total CPC",     f"₹{total_cpc:.3f}")
            m5.metric("Shift Yield",   f"{shift_yield} pcs")

        routing_rows.append({
            "Op No.":         f"{op_num:02d}",
            "Operation":      op_name,
            "Machine":        machine,
            "Cycle Time (min)": cycle_time,
            "Tool Cost/Batch": tool_cost,
            "Machine Rate (₹/hr)": rate,
            "Mach. Cost/pc (₹)":  mach_cost_pc,
            "Tool Cost/pc (₹)":   tool_cost_pc,
            "Total CPC (₹)":      total_cpc,
            "Shift Yield (pcs)":  shift_yield,
            "Remarks":            st.session_state.get(f"rem_{op_num}", ""),
        })

    df = pd.DataFrame(routing_rows)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2: SUMMARY & COST
# ════════════════════════════════════════════════════════════════════════════
with tab_summary:
    st.subheader("Process summary")

    # KPI strip
    total_ct    = df["Cycle Time (min)"].sum()
    total_cpc   = df["Total CPC (₹)"].sum()
    total_batch = total_cpc * batch_size
    bottleneck  = df.loc[df["Cycle Time (min)"].idxmax(), "Operation"]
    bottleneck_ct = df["Cycle Time (min)"].max()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Cycle Time",    f"{total_ct:.1f} min")
    k2.metric("Total CPC",           f"₹{total_cpc:.2f}")
    k3.metric("Batch Cost (est.)",   f"₹{total_batch:,.0f}")
    k4.metric("Bottleneck Op",       bottleneck, delta=f"{bottleneck_ct:.1f} min", delta_color="inverse")

    st.markdown("---")

    # Bar chart — cycle time by operation
    st.markdown("**Cycle time by operation (min)**")
    chart_df = df[["Op No.", "Operation", "Cycle Time (min)"]].copy()
    chart_df["Label"] = chart_df["Op No."] + " " + chart_df["Operation"].str[:25]
    st.bar_chart(chart_df.set_index("Label")["Cycle Time (min)"])

    st.markdown("---")

    # Full routing table
    st.markdown("**Full routing card**")
    st.dataframe(
        df.set_index("Op No."),
        use_container_width=True,
        height=500
    )

    st.markdown("---")

    # Export
    st.markdown("**Export**")
    ex1, ex2 = st.columns(2)

    with ex1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Routing Card (CSV)",
            data=csv,
            file_name=f"{doc_num}_{part_name}_routing.csv",
            mime="text/csv"
        )

    with ex2:
        # Build a simple text summary
        lines = [
            f"ROUTING CARD — {part_name}",
            f"Document No: {doc_num} | Customer: {customer_name} | Rev: {rev_no} | Date: {doc_date}",
            f"Big End Ø: {finish_dia_be}mm | Small End Ø: {finish_dia_se}mm | Thickness: {thickness}mm | Length: {length}mm",
            f"Batch: {batch_size} pcs | Total Cycle Time: {total_ct:.1f} min | Total CPC: ₹{total_cpc:.2f}",
            "",
            f"{'Op':>4}  {'Operation':<45}  {'Machine':<40}  {'CT(min)':>8}  {'CPC(₹)':>8}",
            "-" * 115,
        ]
        for _, row in df.iterrows():
            lines.append(f"{row['Op No.']:>4}  {row['Operation']:<45}  {row['Machine']:<40}  {row['Cycle Time (min)']:>8.1f}  {row['Total CPC (₹)']:>8.3f}")
        lines += ["", f"TOTAL{'':<84}  {total_ct:>8.1f}  {total_cpc:>8.3f}"]
        txt = "\n".join(lines).encode("utf-8")

        st.download_button(
            label="⬇️ Download Summary (TXT)",
            data=txt,
            file_name=f"{doc_num}_{part_name}_summary.txt",
            mime="text/plain"
        )

# ════════════════════════════════════════════════════════════════════════════
# TAB 3: ADMIN — EDIT MASTERS
# ════════════════════════════════════════════════════════════════════════════
with tab_admin:
    st.subheader("⚙️ Admin — master data editor")
    st.warning("Changes here update the JSON files on disk. Reload the app after saving to apply.")

    a1, a2 = st.tabs(["Operations master", "Machines master"])

    with a1:
        st.markdown("**Current operations.json**")
        ops_df = pd.DataFrame(ops_master)
        edited_ops = st.data_editor(
            ops_df,
            use_container_width=True,
            num_rows="dynamic",
            key="ops_editor"
        )
        if st.button("💾 Save operations.json"):
            with open(os.path.join(BASE_DIR, "operations.json"), "w") as f:
                json.dump(edited_ops.to_dict(orient="records"), f, indent=2)
            st.success("operations.json saved. Click the ↻ reload button in Streamlit to apply.")
            st.cache_data.clear()

    with a2:
        st.markdown("**Current machines.json**")
        mac_df = pd.DataFrame(machines_raw)
        edited_mac = st.data_editor(
            mac_df,
            use_container_width=True,
            num_rows="dynamic",
            key="mac_editor"
        )
        if st.button("💾 Save machines.json"):
            with open(os.path.join(BASE_DIR, "machines.json"), "w") as f:
                json.dump(edited_mac.to_dict(orient="records"), f, indent=2)
            st.success("machines.json saved. Click the ↻ reload button in Streamlit to apply.")
            st.cache_data.clear()
