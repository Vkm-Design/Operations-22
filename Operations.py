import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import csv

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

class ConRodPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Con Rod Process Planner & Routing Engine")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f4f6f9")
        
        self.operation_state = []
        self.hrc_correction = {"rpm": 1.0, "feed": 1.0}
        
        self.create_styles()
        self.build_ui()
        self.update_hrc_correction()
        self.build_initial_state()
        self.recalculate_engine()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Card.TFrame", background="#ffffff", borderwidth=1, relief="solid")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background="#ffffff")

    def build_ui(self):
        # --- Top Header Banner ---
        header_frame = tk.Frame(self.root, bg="#1e3a8a", padding=15)
        header_frame.pack(fill="x", side="top", padx=15, pady=10)
        
        lbl_title = tk.Label(header_frame, text="⚙️ Con Rod Process Planner & Routing Engine", 
                             font=("Segoe UI", 16, "bold"), fg="white", bg="#1e3a8a")
        lbl_title.pack(side="left", anchor="w")
        
        btn_csv = tk.Button(header_frame, text="📥 Download Routing Card (CSV)", bg="#0d9488", fg="white",
                            font=("Segoe UI", 10, "bold"), command=self.download_csv, relief="flat", padx=10)
        btn_csv.pack(side="right")

        # --- Main Layout Grid ---
        main_pane = tk.PanedWindow(self.root, orient="horizontal", bg="#f4f6f9", sashrelief="raised", sashwidth=4)
        main_pane.pack(fill="both", expand=True, padx=15, pady=5)
        
        # --- Left Sidebar Scrollable Inputs ---
        sidebar_canvas = tk.Canvas(main_pane, width=320, bg="#f4f6f9", highlightthickness=0)
        sidebar_scroll = ttk.Scrollbar(main_pane, orient="vertical", command=sidebar_canvas.yview)
        self.sidebar = tk.Frame(sidebar_canvas, bg="#f4f6f9")
        self.sidebar.bind("<Configure>", lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        
        main_pane.add(sidebar_canvas)
        main_pane.add(sidebar_scroll)
        
        # --- Right Main Panel ---
        right_panel = tk.Frame(main_pane, bg="#f4f6f9")
        main_pane.add(right_panel)

        # Build Sidebar Widgets
        self.build_sidebar_inputs()
        
        # Build Summary KPIs
        kpi_frame = tk.Frame(right_panel, bg="#f4f6f9")
        kpi_frame.pack(fill="x", pady=(0, 10))
        
        self.kpi_cycle_lbl = tk.Label(kpi_frame, text="Total Cycle Time\n0.00 Mins", font=("Segoe UI", 13, "bold"),
                                      bg="#ffffff", relief="groove", bd=2, width=25, pady=10)
        self.kpi_cycle_lbl.pack(side="left", padx=(0, 15))
        
        self.kpi_yield_lbl = tk.Label(kpi_frame, text="Avg Shift Capacity\n0 pcs", font=("Segoe UI", 13, "bold"),
                                      bg="#ffffff", relief="groove", bd=2, width=25, pady=10, fg="#8b5cf6")
        self.kpi_yield_lbl.pack(side="left")

        # --- Operational Central Grid Table View ---
        table_card = ttk.Frame(right_panel, style="Card.TFrame")
        table_card.pack(fill="both", expand=True, pady=5)
        
        table_header = tk.Label(table_card, text="📄 Process Routing Card — 22 Operations (Editable Parameters Below)", 
                                font=("Segoe UI", 11, "bold"), bg="#ffffff", anchor="w", padx=10, pady=8)
        table_header.pack(fill="x")
        
        table_frame = tk.Frame(table_card, bg="#ffffff")
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars for Data Tree
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("Op", "OpName", "Machine", "MachCost", "PartsLoaded", "OpTime", "LoadUnload", "CycleMin", "PartsHr", "ToolCost", "ToolLife", "Unit", "Regrinds", "ToolCostPc")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                 xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set, selectmode="browse")
        
        scroll_x.config(command=self.tree.xview)
        scroll_y.config(command=self.tree.yview)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Layout Headings
        headers = {
            "Op": "Op #", "OpName": "Operation Name", "Machine": "Machine Type", "MachCost": "M/c Cost (Lakh)",
            "PartsLoaded": "Loaded", "OpTime": "Mach (s)", "LoadUnload": "L/U (s)", "CycleMin": "Cycle (m)",
            "PartsHr": "Pcs/Hr", "ToolCost": "Tool Cost (₹)", "ToolLife": "Life", "Unit": "Unit",
            "Regrinds": "Regrinds", "ToolCostPc": "Cost/Pc (₹)"
        }
        for col, txt in headers.items():
            self.tree.heading(col, text=txt, anchor="center")
            self.tree.column(col, width=70 if len(col)<7 else 130, anchor="center" if col!="OpName" else "w")
            
        self.tree.bind("<Double-1>", self.on_double_click_edit)

        # --- Inline Text-Based Analytics Panel ---
        charts_frame = tk.Frame(right_panel, bg="#f4f6f9")
        charts_frame.pack(fill="x", pady=10)
        
        self.txt_chart_cycle = tk.Text(charts_frame, height=12, width=65, font=("Consolas", 9.5), bg="#ffffff", bd=1, relief="solid")
        self.txt_chart_cycle.pack(side="left", padx=(0, 15), fill="x", expand=True)
        
        self.txt_chart_cost = tk.Text(charts_frame, height=12, width=65, font=("Consolas", 9.5), bg="#ffffff", bd=1, relief="solid")
        self.txt_chart_cost.pack(side="right", fill="x", expand=True)

    def build_sidebar_inputs(self):
        def create_section(parent, name):
            f = tk.LabelFrame(parent, text=name, font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#0f172a", padx=10, pady=10)
            f.pack(fill="x", pady=8, padx=5)
            return f

        # Section 1: Metadata
        sec1 = create_section(self.sidebar, "📋 Document Metadata")
        self.inputs = {}
        for label_text, var_key, default in [("Document Number", "docNum", "DOC-2026-001"), 
                                             ("Part Name", "partName", "Con Rod — SCr420HV"), 
                                             ("Customer Name", "customerName", "Global Corp")]:
            tk.Label(sec1, text=label_text, font=("Segoe UI", 9), bg="#ffffff", fg="#64748b").pack(anchor="w")
            ent = ttk.Entry(sec1)
            ent.insert(0, default)
            ent.pack(fill="x", pady=(2, 6))
            self.inputs[var_key] = ent

        # Section 2: Material & Dynamic Rates
        sec2 = create_section(self.sidebar, "🪵 Material & Shift Settings")
        tk.Label(sec2, text="Material Grade", font=("Segoe UI", 9), bg="#ffffff", fg="#64748b").pack(anchor="w")
        self.mat_grade_combo = ttk.Combobox(sec2, values=["Steel (up to 30 HRC)", "Steel (30–40 HRC)"], state="readonly")
        self.mat_grade_combo.current(0)
        self.mat_grade_combo.pack(fill="x", pady=(2, 6))
        self.mat_grade_combo.bind("<<ComboboxSelected>>", lambda e: self.trigger_recalculation())

        for label_text, var_key, default in [("Batch Size (pcs)", "batchSize", "500"),
                                             ("Base Hourly Rate (INR/hr)", "baseHourlyRate", "500"),
                                             ("Shift Efficiency (%)", "efficiency", "90")]:
            tk.Label(sec2, text=label_text, font=("Segoe UI", 9), bg="#ffffff", fg="#64748b").pack(anchor="w")
            ent = ttk.Entry(sec2)
            ent.insert(0, default)
            ent.pack(fill="x", pady=(2, 6))
            ent.bind("<FocusOut>", lambda e: self.trigger_recalculation())
            self.inputs[var_key] = ent

        # Section 3: Component Sizing Engine Parameters
        sec3 = create_section(self.sidebar, "📐 Component Dimensions")
        for label_text, var_key, default in [("Big End Diameter (mm)", "finishDia1", "38.0"),
                                             ("Big End Thickness (mm)", "thicknessD1", "16.0"),
                                             ("Small End Diameter (mm)", "finishDia2", "14.0"),
                                             ("Small End Thickness (mm)", "thicknessD2", "16.0"),
                                             ("Oil Hole Depth (mm)", "oilHoleDepth", "3.0")]:
            tk.Label(sec3, text=label_text, font=("Segoe UI", 9), bg="#ffffff", fg="#64748b").pack(anchor="w")
            ent = ttk.Entry(sec3)
            ent.insert(0, default)
            ent.pack(fill="x", pady=(2, 6))
            ent.bind("<FocusOut>", lambda e: self.trigger_recalculation())
            self.inputs[var_key] = ent

    def update_hrc_correction(self):
        grade = self.mat_grade_combo.get()
        if "30–40" in grade:
            self.hrc_correction = {"rpm": 0.90, "feed": 0.95}
        else:
            self.hrc_correction = {"rpm": 1.0, "feed": 1.0}

    def build_initial_state(self):
        f_dia1 = float(self.inputs["finishDia1"].get() or 38.0)
        f_dia2 = float(self.inputs["finishDia2"].get() or 14.0)
        t_d1 = float(self.inputs["thicknessD1"].get() or 16.0)
        t_d2 = float(self.inputs["thicknessD2"].get() or 16.0)
        oh_depth = float(self.inputs["oilHoleDepth"].get() or 3.0)

        # Smart Engine logic placeholder for Op3 mapping
        calculated_op3_time = max(25.0, round((f_dia1 * 0.4) + (f_dia2 * 0.5) + (t_d1 * 0.3), 1))

        self.operation_state = []
        for idx, name in enumerate(OPERATION_NAMES, 1):
            machine = "Manual"
            mc_lakh = 0
            parts_loaded = 1
            op_time = 60
            lu_time = 5
            tool_cost = 1200
            tool_life = 250
            unit = "Parts"
            regrinds = 2
            regrind_cost = 150
            is_manual = False

            # Differentiate defaults per specific real ops mapping
            if idx == 1:
                machine, op_time, lu_time, tool_cost, is_manual = "Manual", 0, 0, 0, True
            elif idx in [2, 8]:
                machine, parts_loaded, op_time, lu_time, tool_cost, tool_life = "SDG (Ø600)- For CR Thickness Grinding", 2, 12, 0, 40000, 150000
            elif idx == 3:
                machine, op_time, lu_time, tool_cost, tool_life = "Makino", calculated_op3_time, 0, 8500, 500
            elif idx == 4:
                machine, op_time, lu_time, tool_cost, tool_life = "Sansera Horizontal Machine", 48, 5, 800, 200
            elif idx in [5, 6, 7]:
                machine = "SQF" if idx==5 else ("Shot Blasting M/c" if idx==6 else "IH M/c")
                op_time, lu_time, tool_cost, is_manual = 0, 0, 0, True
            elif idx == 9:
                machine, op_time, lu_time, tool_cost, tool_life, unit = "SFB 02- For CR Fine Boring with Index table & NT", 15, 0, 3500, 45, "Mtr"
            elif idx == 10:
                machine, op_time, lu_time, tool_cost, tool_life, unit = "SHD 03/ SID- For CR Oil Hole Drilling", 8, 5, 1000, 30, "Mtr"
            elif idx == 11:
                machine, op_time, lu_time, tool_cost, tool_life = "Deburring Station", 10, 0, 0, 1000
            elif idx == 12:
                machine, op_time, lu_time, tool_cost, tool_life = "Drilling Machine", 6, 6, 350, 400
            elif idx in [13, 14]:
                machine, parts_loaded, op_time, tool_cost, tool_life = "SVH- For CR Vertical Honing/Big End Honing", 6, 64, 21600 if idx==13 else 180000, 40000 if idx==13 else 200000
            elif idx in [15, 16, 17, 18, 19, 20, 21]:
                machine = "MPI" if idx==15 else ("Demagnetiser" if idx==16 else ("CLEANING 01- Cleantech" if idx==17 else ("Laser Marking M/c" if idx==20 else "Manual")))
                op_time, lu_time, tool_cost = (10 if idx in [15,16,18] else (8 if idx==17 else (15 if idx==19 else 6))), 0, 0
            elif idx == 22:
                machine, op_time, lu_time, tool_cost, is_manual = "Manual", 0, 0, 0, True

            mc_lakh = MACHINE_COST_DEFAULTS.get(machine, 0)
            
            self.operation_state.append({
                "opIdx": idx, "name": name, "machine": machine, "machineCostLakh": mc_lakh,
                "partsLoaded": parts_loaded, "opTimeSec": op_time, "loadUnloadSec": lu_time,
                "newToolCost": tool_cost, "toolLifeVal": tool_life, "unit": unit,
                "regrinds": regrinds, "regrindCost": regrind_cost, "isManual": is_manual
            })

    def trigger_recalculation(self):
        self.update_hrc_correction()
        self.recalculate_engine()

    def recalculate_engine(self):
        try:
            eff = float(self.inputs["efficiency"].get() or 90) / 100.0
            hourly_rate = float(self.inputs["baseHourlyRate"].get() or 500)
        except ValueError:
            return

        total_cycle_min = 0.0
        
        # Clear Data Window
        for row in self.tree.get_children():
            self.tree.delete(row)

        for op in self.operation_state:
            if op["isManual"] or op["opTimeSec"] == 0:
                cycle_min = 0.0
                parts_per_hr = 0.0
                tool_cost_pc = 0.0
            else:
                # Engineering core calculations
                total_station_sec = (op["opTimeSec"] / op["partsLoaded"]) + op["loadUnloadSec"]
                cycle_min = total_station_sec / 60.0
                parts_per_hr = (60.0 / cycle_min) * eff if cycle_min > 0 else 0
                
                # Tooling Life Cost breakdown
                total_life = op["toolLifeVal"] * (1 + op["regrinds"])
                if total_life > 0 and op["newToolCost"] > 0:
                    total_tool_expense = op["newToolCost"] + (op["regrinds"] * op["regrindCost"])
                    tool_cost_pc = total_tool_expense / total_life
                else:
                    tool_cost_pc = 0.0

            total_cycle_min += cycle_min
            op["calculated_cycle"] = cycle_min
            op["calculated_cpc"] = tool_cost_pc

            # Inject into UI Tree
            self.tree.insert("", "end", values=(
                f"Op {op['opIdx']:02d}", op["name"], op["machine"], op["machineCostLakh"],
                op["partsLoaded"], op["opTimeSec"], op["loadUnloadSec"], f"{cycle_min:.2f}",
                f"{parts_per_hr:.1f}", op["newToolCost"], op["toolLifeVal"], op["unit"],
                op["regrinds"], f"₹{tool_cost_pc:.2f}"
            ))

        # Update KPIs
        shift_capacity = (480.0 / total_cycle_min) * eff if total_cycle_min > 0 else 0
        self.kpi_cycle_lbl.config(text=f"Total Cycle Time\n{total_cycle_min:.2f} Mins")
        self.kpi_yield_lbl.config(text=f"Avg Shift Capacity\n{int(shift_capacity)} Pcs")
        
        self.render_text_charts()

    def on_double_click_edit(self, event):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        
        # Identity parsing
        op_str = self.tree.item(item, "values")[0]
        op_idx = int(op_str.replace("Op ", ""))
        op_data = next(o for o in self.operation_state if o["opIdx"] == op_idx)
        
        # Simple modal window input pop
        pop = tk.Toplevel(self.root)
        pop.title(f"Modify Operation {op_idx:02d}")
        pop.geometry("350x250")
        pop.resizable(False, False)
        
        tk.Label(pop, text=f"Edit values for: {op_data['name'][:30]}...", font=("Segoe UI", 9, "italic")).pack(pady=5)
        
        fields = [("Machining Time (Sec)", "opTimeSec"), ("Load / Unload Time (Sec)", "loadUnloadSec"), ("New Tool Cost (₹)", "newToolCost")]
        entries = {}
        for lbl, key in fields:
            f = tk.Frame(pop)
            f.pack(fill="x", padx=20, pady=4)
            tk.Label(f, text=lbl, width=22, anchor="w").pack(side="left")
            e = ttk.Entry(f)
            e.insert(0, str(op_data[key]))
            e.pack(side="right", expand=True, fill="x")
            entries[key] = e
            
        def save():
            try:
                for lbl, key in fields:
                    op_data[key] = float(entries[key].get()) if "Cost" in lbl or "Time" in key else int(entries[key].get())
                pop.destroy()
                self.recalculate_engine()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric parameters.")

        tk.Button(pop, text="💾 Save & Update Engine", bg="#2563eb", fg="white", command=save, relief="flat").pack(pady=15)

    def render_text_charts(self):
        # Render Horizontal Text-based bars for cycle time 
        self.txt_chart_cycle.config(state="normal")
        self.txt_chart_cycle.delete("1.0", tk.END)
        self.txt_chart_cycle.insert(tk.END, "⏱️ Cycle Time Bar-Chart breakdown (Seconds):\n" + "-"*55 + "\n")
        
        for op in self.operation_state:
            if op["opTimeSec"] > 0:
                bar_len = min(30, int(op["opTimeSec"] / 3))
                bar = "█" * bar_len
                self.txt_chart_cycle.insert(tk.END, f"Op {op['opIdx']:02d}: {bar:<30} {op['opTimeSec']}s\n")
        self.txt_chart_cycle.config(state="disabled")

        # Render Horizontal Text-based bars for CPC Tooling Cost
        self.txt_chart_cost.config(state="normal")
        self.txt_chart_cost.delete("1.0", tk.END)
        self.txt_chart_cost.insert(tk.END, "💰 Tooling Consumable Cost (₹ per piece):\n" + "-"*55 + "\n")
        
        for op in self.operation_state:
            if op["calculated_cpc"] > 0:
                bar_len = min(30, int(op["calculated_cpc"] * 2))
                bar = "▓" * bar_len
                self.txt_chart_cost.insert(tk.END, f"Op {op['opIdx']:02d}: {bar:<30} ₹{op['calculated_cpc']:.2f}/pc\n")
        self.txt_chart_cost.config(state="disabled")

    def download_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
            
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Document Metadata Sheet Summary"])
            writer.writerow(["Doc Number", self.inputs["docNum"].get()])
            writer.writerow(["Part Name", self.inputs["partName"].get()])
            writer.writerow([])
            writer.writerow(["Op #", "Operation Name", "Machine Type", "Machine Cost (Lakh)", "Parts Loaded", "Mach Time (s)", "L/U Time (s)", "Calculated Cycle (min)", "Tool Cost/pc (INR)"])
            
            for op in self.operation_state:
                writer.writerow([
                    op["opIdx"], op["name"], op["machine"], op["machineCostLakh"],
                    op["partsLoaded"], op["opTimeSec"], op["loadUnloadSec"],
                    f"{op['calculated_cycle']:.2f}", f"{op['calculated_cpc']:.2f}"
                ])
                
        messagebox.showinfo("Success", f"Process Routing sheet successfully exported to:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConRodPlannerApp(root)
    root.mainloop()
