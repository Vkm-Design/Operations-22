<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Engineering Process Planner & Routing Engine</title>
    <meta name="description" content="A premium offline manufacturing process planner and routing engine with automated cycle time, tool wear, and cost calculations for 22 operations.">
    <style>
        :root {
            --bg-primary: #f4f6f9;
            --bg-card: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --accent: #0f766e;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --radius: 12px;
            --transition: all 0.2s ease-in-out;
            --theme-process: #dbeafe;
            --theme-machining: #ccfbf1;
            --theme-tooling: #dcfce7;
            --theme-outputs: #f3e8ff;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 20px;
        }

        .container { max-width: 1920px; margin: 0 auto; }

        header {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
            color: white;
            padding: 30px;
            border-radius: var(--radius);
            margin-bottom: 24px;
            box-shadow: var(--shadow-lg);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        header h1 { font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        header p { color: #94a3b8; font-size: 0.95rem; margin-top: 4px; }

        .layout-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 24px;
        }

        @media (max-width: 1300px) { .layout-grid { grid-template-columns: 1fr; } }

        aside { display: flex; flex-direction: column; gap: 20px; }

        .card {
            background-color: var(--bg-card);
            border-radius: var(--radius);
            padding: 24px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            transition: var(--transition);
        }

        .card:hover { box-shadow: 0 10px 20px -5px rgb(0 0 0 / 0.05); }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: #0f172a;
            border-bottom: 2px solid var(--bg-primary);
            padding-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-group { margin-bottom: 14px; }

        .form-group label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }

        .form-control {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            color: var(--text-primary);
            background-color: #f8fafc;
            transition: var(--transition);
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            background-color: #ffffff;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }

        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        main { display: flex; flex-direction: column; gap: 24px; }

        .kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        @media (max-width: 600px) { .kpi-row { grid-template-columns: 1fr; } }

        .kpi-card {
            background-color: var(--bg-card);
            border-left: 5px solid var(--primary);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
        }

        .kpi-card.cpc { border-left-color: #0d9488; }
        .kpi-card.yield { border-left-color: #8b5cf6; }
        .kpi-label { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
        .kpi-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-top: 6px; }

        .table-responsive {
            width: 100%;
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background-color: var(--bg-card);
            box-shadow: var(--shadow);
        }

        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.83rem; }

        .group-header {
            text-align: center;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            padding: 8px 4px;
            border-bottom: 2px solid var(--border);
        }

        .gh-id    { background-color: #f1f5f9;              color: #334155; }
        .gh-process { background-color: var(--theme-process);  color: #1e40af; }
        .gh-machine { background-color: #e0f2fe;              color: #0369a1; }
        .gh-cycle   { background-color: var(--theme-machining); color: #115e59; }
        .gh-tooling { background-color: var(--theme-tooling);   color: #166534; }
        .gh-outputs { background-color: var(--theme-outputs);   color: #6b21a8; }
        .gh-cpc     { background-color: #fdf4ff;              color: #7c3aed; }

        th {
            background-color: #f8fafc;
            color: var(--text-secondary);
            font-weight: 600;
            padding: 9px 7px;
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
        }

        td {
            padding: 5px 7px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
            vertical-align: middle;
        }

        tr:last-child td { border-bottom: none; }
        tr:hover td { background-color: #f8fafc; }

        .op-badge {
            background-color: #e2e8f0;
            color: #334155;
            padding: 3px 6px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.72rem;
        }

        .btn-group { display: flex; gap: 12px; }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: var(--primary);
            color: white;
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: var(--transition);
        }

        .btn:hover { background-color: var(--primary-hover); }
        .btn-success { background-color: #0d9488; }
        .btn-success:hover { background-color: #0f766e; }

        .bar-chart-list { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }

        .bar-chart-row { display: flex; align-items: center; font-size: 0.8rem; }

        .bar-chart-label {
            width: 180px;
            font-weight: 600;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-right: 12px;
        }

        .bar-chart-container {
            flex-grow: 1;
            background-color: #f1f5f9;
            height: 16px;
            border-radius: 4px;
            overflow: hidden;
        }

        .bar-chart-fill {
            background-color: var(--primary);
            height: 100%;
            border-radius: 4px;
            transition: width 0.4s ease-out;
        }

        .bar-chart-row:hover .bar-chart-fill { filter: brightness(1.1); }

        .bar-chart-value {
            width: 80px;
            text-align: right;
            font-weight: 700;
            color: var(--text-primary);
            padding-left: 12px;
        }

        .chart-cpc-fill { background-color: #0d9488; }

        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 1000px) { .charts-grid { grid-template-columns: 1fr; } }

        .chart-card {
            background-color: var(--bg-card);
            border-radius: var(--radius);
            padding: 24px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }

        /* Inline editable table inputs */
        .ti {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 3px 4px;
            width: 100%;
            color: inherit;
            font-family: inherit;
            font-size: 0.82rem;
            transition: var(--transition);
        }

        .ti:hover { background-color: #f1f5f9; border-color: var(--border); }

        .ti:focus {
            background-color: #ffffff;
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
        }

        .ti-num { text-align: right; max-width: 70px; }

        .ti-sel {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 3px;
            font-size: 0.8rem;
            cursor: pointer;
        }

        .ti-sel:hover { background-color: #f1f5f9; border-color: var(--border); }
        .ti-sel:focus { background-color: #ffffff; outline: none; border-color: var(--primary); }

        /* Column group coloring on cells */
        td.col-machine  { background-color: #f0f9ff; }
        td.col-cycle    { background-color: #f0fdfa; font-weight: 700; }
        td.col-mcost    { background-color: #e0f2fe; }

    </style>
</head>
<body>
<div class="container">

    <!-- ── Header ── -->
    <header>
        <div>
            <h1>⚙️ Engineering Process Planner & Routing Engine</h1>
            <p>Spreadsheet-style offline process card with INR machining and tooling cost analysis</p>
        </div>
        <div class="btn-group">
            <button id="downloadCsvBtn" class="btn btn-success">📥 Download Routing Card (CSV)</button>
        </div>
    </header>

    <div class="layout-grid">
        <!-- ── Sidebar ── -->
        <aside>
            <section class="card">
                <h2 class="card-title">📋 Document Metadata</h2>
                <div class="form-group">
                    <label for="docNum">Document Number</label>
                    <input type="text" id="docNum" class="form-control" value="DOC-2026-001">
                </div>
                <div class="form-group">
                    <label for="partName">Part Name</label>
                    <input type="text" id="partName" class="form-control" value="Main Shaft / Valve Body">
                </div>
                <div class="form-group">
                    <label for="customerName">Customer Name</label>
                    <input type="text" id="customerName" class="form-control" value="Global Machining Corp">
                </div>
            </section>

            <section class="card">
                <h2 class="card-title">🪵 Material & Rate</h2>
                <div class="form-group">
                    <label for="materialGrade">Material Grade</label>
                    <select id="materialGrade" class="form-control">
                        <option value="Carbon Steel">Carbon Steel</option>
                        <option value="Aluminium">Aluminium</option>
                        <option value="Alloy Steel" selected>Alloy Steel</option>
                        <option value="Stainless Steel">Stainless Steel</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="hardnessValue">Hardness</label>
                    <input type="text" id="hardnessValue" class="form-control" value="32 HRC">
                </div>
                <div class="form-group">
                    <label for="batchSize">Batch Size (pcs)</label>
                    <input type="number" id="batchSize" class="form-control" value="500" min="1">
                </div>
                <div class="form-group">
                    <label for="baseHourlyRate">Base Hourly Rate (INR/hr)</label>
                    <input type="number" id="baseHourlyRate" class="form-control" value="500" min="1" step="10">
                </div>
            </section>

            <section class="card">
                <h2 class="card-title">📐 D1 & D2 Sizing</h2>
                <h3 style="font-size:0.82rem;margin-bottom:6px;color:var(--primary);">Diameter 1 (D1)</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="finishDia1">Finish D1 (mm)</label>
                        <input type="number" id="finishDia1" class="form-control" value="35.0" step="0.1">
                    </div>
                    <div class="form-group">
                        <label for="toleranceD1">Tolerance D1</label>
                        <input type="number" id="toleranceD1" class="form-control" value="0.025" step="0.005">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="inputDia1">Input D1 (mm)</label>
                        <input type="number" id="inputDia1" class="form-control" value="39.0" step="1">
                    </div>
                    <div class="form-group">
                        <label for="thicknessD1">Length D1 (mm)</label>
                        <input type="number" id="thicknessD1" class="form-control" value="40.0" step="1">
                    </div>
                </div>
                <div class="form-group">
                    <label for="surfaceFinishD1">Surface Finish Ra D1</label>
                    <input type="number" id="surfaceFinishD1" class="form-control" value="1.6" step="0.1">
                </div>
                <h3 style="font-size:0.82rem;margin-top:12px;margin-bottom:6px;color:var(--accent);">Diameter 2 (D2)</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="finishDia2">Finish D2 (mm)</label>
                        <input type="number" id="finishDia2" class="form-control" value="25.0" step="0.1">
                    </div>
                    <div class="form-group">
                        <label for="toleranceD2">Tolerance D2</label>
                        <input type="number" id="toleranceD2" class="form-control" value="0.025" step="0.005">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="inputDia2">Input D2 (mm)</label>
                        <input type="number" id="inputDia2" class="form-control" value="0" step="1">
                    </div>
                    <div class="form-group">
                        <label for="thicknessD2">Length D2 (mm)</label>
                        <input type="number" id="thicknessD2" class="form-control" value="20.0" step="1">
                    </div>
                </div>
                <div class="form-group">
                    <label for="surfaceFinishD2">Surface Finish Ra D2</label>
                    <input type="number" id="surfaceFinishD2" class="form-control" value="1.6" step="0.1">
                </div>
            </section>

            <section class="card">
                <h2 class="card-title">🛢️ Oil Hole Spec</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label for="oilHoleQty1">Qty</label>
                        <input type="number" id="oilHoleQty1" class="form-control" value="1" min="0">
                    </div>
                    <div class="form-group">
                        <label for="oilHoleDia1">Dia (mm)</label>
                        <input type="number" id="oilHoleDia1" class="form-control" value="10.0" step="0.5">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="oilHoleDepth1">Depth (mm)</label>
                        <input type="number" id="oilHoleDepth1" class="form-control" value="15.0" step="1">
                    </div>
                    <div class="form-group">
                        <label for="oilHoleFinish1">Finish (Ra)</label>
                        <input type="number" id="oilHoleFinish1" class="form-control" value="3.2" step="0.4">
                    </div>
                </div>
            </section>
        </aside>

        <!-- ── Main Area ── -->
        <main>
            <!-- KPIs -->
            <section class="kpi-row">
                <div class="kpi-card">
                    <span class="kpi-label">Total Cycle Time</span>
                    <span id="kpiCycleTime" class="kpi-value">0.00 Mins</span>
                </div>

                <div class="kpi-card yield">
                    <span class="kpi-label">Avg Shift Capacity</span>
                    <span id="kpiYield" class="kpi-value">0 pcs</span>
                </div>
            </section>

            <!-- Process Routing Card Table -->
            <section class="card" style="padding:0;overflow:hidden;">
                <div style="padding:18px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                    <h2 style="font-size:1.05rem;font-weight:700;color:#0f172a;margin:0;">📄 Process Routing Card — 22 Operations</h2>
                    <span id="metaSummary" style="font-size:0.82rem;font-weight:600;color:var(--text-secondary);"></span>
                </div>

                <div class="table-responsive">
                    <table id="routingTable">
                        <thead>
                            <!-- Group Row -->
                            <tr>
                                <th colspan="2"  class="group-header gh-id">ID</th>
                                <th colspan="2"  class="group-header gh-machine">Machine</th>
                                <th colspan="5"  class="group-header gh-process">Process & Sizing Inputs</th>
                                <th colspan="2"  class="group-header gh-cycle">Cycle Outputs</th>
                                <th colspan="5"  class="group-header gh-tooling">Tooling Inputs (Editable)</th>
                                <th colspan="3"  class="group-header gh-outputs">Tooling Outputs</th>
                            </tr>
                            <!-- Sub-header Row -->
                            <tr>
                                <!-- ID -->
                                <th style="width:42px;">Op #</th>
                                <th style="width:175px;">Operation Name</th>
                                <!-- Machine -->
                                <th style="width:110px;">Machine</th>
                                <th style="width:85px;text-align:right;">Machine Cost (Lakh)</th>
                                <!-- Process & Sizing -->
                                <th style="width:185px;">Process Description</th>
                                <th style="width:58px;text-align:right;">Parts Loaded</th>
                                <th style="width:68px;text-align:right;">Cut Length (mm)</th>
                                <th style="width:60px;text-align:right;">Positions</th>
                                <th style="width:70px;text-align:right;">Op Time (Sec)</th>
                                <th style="width:70px;text-align:right;">Load/Unload (Sec)</th>
                                <!-- Cycle Outputs -->
                                <th style="width:65px;text-align:right;">Cycle (Min)</th>
                                <th style="width:85px;text-align:right;">Mach. Cost (INR/pc)</th>
                                <!-- Tooling Inputs -->
                                <th style="width:82px;text-align:right;">New Tool Cost (₹)</th>
                                <th style="width:70px;text-align:right;">Tool Life</th>
                                <th style="width:60px;">Unit</th>
                                <th style="width:65px;text-align:right;">Regrinds</th>
                                <th style="width:82px;text-align:right;">Regrind Cost (₹)</th>
                                <!-- Tooling Outputs -->
                                <th style="width:80px;text-align:right;">Total Life</th>
                                <th style="width:90px;text-align:right;">Parts Produced</th>
                                <th style="width:82px;text-align:right;">Tool Cost (₹/pc)</th>
                            </tr>
                        </thead>
                        <tbody id="routingTableBody"></tbody>
                    </table>
                </div>
            </section>

            <!-- Charts -->
            <section class="charts-grid">
                <div class="chart-card">
                    <h2 class="card-title">⏱️ Cycle Time per Operation (Min)</h2>
                    <div id="cycleTimeChartList" class="bar-chart-list"></div>
                </div>
                <div class="chart-card">
                    <h2 class="card-title">💰 Stage CPC (₹/pc)</h2>
                    <div id="costChartList" class="bar-chart-list"></div>
                </div>
            </section>
        </main>
    </div>
</div>

<script>
const OPERATION_NAMES = [
    "Inward Inspection Of Forging",
    "Rough Thickness Grinding",
    "Big End Rough Boring, Chamfering (1st side) & Small end Drilling",
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
];

// Default machine costs in Lakh INR per machine type
const MACHINE_COST_DEFAULTS = {
    "Manual":                   0,
    "SDG(Ø600)":               36,
    "CNC VMC":                 60,
    "CNC Lathe":               45,
    "Heat Treat Furnace":      80,
    "Shot Blasting Machine":   18,
    "Induction Heater":        22,
    "Precision Duplex Grinder":50,
    "Special Purpose Drill":   28,
    "Chamfering Machine":      15,
    "Vertical Honing Machine": 35,
    "MPI Equipment":           12,
    "Demagnetiser":             5,
    "Industrial Washing Machine":20,
    "Inspection Fixture":       8,
    "Laser Marker":            25,
};

let operationState = [];

function getMachineCostLakh(machineName) {
    for (const key of Object.keys(MACHINE_COST_DEFAULTS)) {
        if (machineName && machineName.toLowerCase().includes(key.toLowerCase())) {
            return MACHINE_COST_DEFAULTS[key];
        }
    }
    if (MACHINE_COST_DEFAULTS[machineName] !== undefined) return MACHINE_COST_DEFAULTS[machineName];
    return 0;
}

function buildInitialState() {
    const finishDia2  = Math.max(0, parseFloat(document.getElementById('finishDia2').value)  || 0);
    const thicknessD1 = Math.max(0, parseFloat(document.getElementById('thicknessD1').value) || 0);
    const thicknessD2 = Math.max(0, parseFloat(document.getElementById('thicknessD2').value) || 0);
    const inputDia2   = Math.max(0, parseFloat(document.getElementById('inputDia2').value)   || 0);
    const oilHoleQty1  = Math.max(0, parseInt(document.getElementById('oilHoleQty1').value)  || 0);
    const oilHoleDia1  = Math.max(0, parseFloat(document.getElementById('oilHoleDia1').value)|| 0);
    const oilHoleDepth1= Math.max(0, parseFloat(document.getElementById('oilHoleDepth1').value)||0);
    const sfD2 = document.getElementById('surfaceFinishD2').value;

    operationState = OPERATION_NAMES.map((name, idx) => {
        const opIdx = idx + 1;
        let machine = "VMC", desc = "Standard process step";
        let partsLoaded = 1, cutLength = 0, positions = 1;
        let opTimeSec = 90, loadUnloadSec = 0;
        let newToolCost = 1000, toolLifeVal = 100, unit = "Mtr";
        let regrinds = 3, regrindCost = 100;
        let isManual = false;

        switch (opIdx) {
            case 1:
                machine = "Manual"; isManual = true;
                desc = "Visual & dimensional inspection of incoming raw forging batch.";
                opTimeSec = 0; loadUnloadSec = 0;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 2:
                machine = "SDG(Ø600)";
                desc = "Rough grind faces to remove raw scale and establish D1 thickness reference.";
                partsLoaded = 2; opTimeSec = 12; loadUnloadSec = 0; cutLength = 10;
                newToolCost = 1200; toolLifeVal = 100; unit = "Mtr"; regrinds = 3; regrindCost = 100;
                break;
            case 3:
                machine = "CNC VMC";
                desc = `Rough bore Big End to Ø${finishDia2}mm, drill Small End, and chamfer 1st side.`;
                let vmcMin = inputDia2 === 0 ? (finishDia2 * 0.12) * (thicknessD2 / 10)
                                             : ((finishDia2 - inputDia2) * 0.06) * (thicknessD2 / 10);
                opTimeSec = Math.max(10, Math.round(vmcMin * 60));
                loadUnloadSec = 5;
                newToolCost = 4500; toolLifeVal = 120; unit = "Min"; regrinds = 3; regrindCost = 400;
                break;
            case 4:
                machine = "CNC Lathe";
                desc = "Setup on fixture and chamfer the opposing (second) side of the Big End bore.";
                opTimeSec = 48; loadUnloadSec = 5;
                newToolCost = 800; toolLifeVal = 200; unit = "Min"; regrinds = 2; regrindCost = 80;
                break;
            case 5:
                machine = "Heat Treat Furnace";
                desc = "Case carburize, harden, and temper component to target hardness.";
                opTimeSec = 300; loadUnloadSec = 0;
                newToolCost = 1000; toolLifeVal = 10000; unit = "Min"; regrinds = 1; regrindCost = 0;
                break;
            case 6:
                machine = "Shot Blasting Machine";
                desc = "Shot blast for scaling removal and surface cleaning post heat-treatment.";
                opTimeSec = 90; loadUnloadSec = 0;
                newToolCost = 500; toolLifeVal = 1000; unit = "Min"; regrinds = 1; regrindCost = 0;
                break;
            case 7:
                machine = "Induction Heater";
                desc = "Locally induction-soften Small End core area.";
                opTimeSec = 60; loadUnloadSec = 5;
                newToolCost = 2000; toolLifeVal = 5000; unit = "Min"; regrinds = 1; regrindCost = 0;
                break;
            case 8:
                machine = "Precision Duplex Grinder";
                desc = `Precision duplex grind faces to final D1 thickness specification (${thicknessD1}mm).`;
                opTimeSec = Math.max(10, Math.round((1.0 + thicknessD1 * 0.03) * 60));
                loadUnloadSec = 5; cutLength = 20;
                newToolCost = 6000; toolLifeVal = 150; unit = "Mtr"; regrinds = 6; regrindCost = 300;
                break;
            case 9:
                machine = "CNC Lathe";
                desc = "Finish hard bore Big End and Small End bores after heat treatment.";
                let hbMin = Math.max(1.5, (finishDia2 * 0.09) * (thicknessD2 / 10));
                opTimeSec = Math.max(10, Math.round(hbMin * 60));
                loadUnloadSec = 5;
                newToolCost = 3500; toolLifeVal = 80; unit = "Min"; regrinds = 2; regrindCost = 300;
                break;
            case 10:
                machine = "Special Purpose Drill";
                if (oilHoleQty1 > 0) {
                    desc = `Drill ${oilHoleQty1} oil hole(s) Ø${oilHoleDia1}mm to depth ${oilHoleDepth1}mm & chamfer.`;
                    opTimeSec = Math.max(5, Math.round(oilHoleQty1 * oilHoleDepth1 * 0.06 * 60));
                    newToolCost = 1500; toolLifeVal = 120; unit = "Min"; regrinds = 4; regrindCost = 150;
                } else {
                    desc = "No oil hole 1 configured – step skipped.";
                    opTimeSec = 0; newToolCost = 0; toolLifeVal = 0; regrinds = 0;
                }
                loadUnloadSec = 5;
                break;
            case 11:
                machine = "Manual";
                if (oilHoleQty1 > 0) {
                    desc = "Debur internal intersections of oil holes manually.";
                    opTimeSec = 60;
                    newToolCost = 100; toolLifeVal = 1000; unit = "Min"; regrinds = 1; regrindCost = 0;
                } else {
                    desc = "No oil hole deburring needed.";
                    opTimeSec = 0; newToolCost = 0; toolLifeVal = 0; regrinds = 0;
                }
                loadUnloadSec = 0;
                break;
            case 12:
                machine = "Chamfering Machine";
                desc = "Precision chamfer Small End bore entry and exit edges.";
                opTimeSec = 48; loadUnloadSec = 5;
                newToolCost = 800; toolLifeVal = 300; unit = "Min"; regrinds = 3; regrindCost = 80;
                break;
            case 13:
                machine = "Vertical Honing Machine";
                desc = `Hone Big End bore to final size tolerance (Ra ${sfD2}).`;
                opTimeSec = 132; loadUnloadSec = 10;
                newToolCost = 8000; toolLifeVal = 400; unit = "Min"; regrinds = 5; regrindCost = 500;
                break;
            case 14:
                machine = "Vertical Honing Machine";
                desc = "Hone Small End bore to final size tolerance.";
                opTimeSec = 120; loadUnloadSec = 10;
                newToolCost = 8000; toolLifeVal = 400; unit = "Min"; regrinds = 5; regrindCost = 500;
                break;
            case 15:
                machine = "MPI Equipment";
                desc = "100% Magnetic Particle Inspection for micro-cracks.";
                opTimeSec = 72; loadUnloadSec = 5;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 16:
                machine = "Demagnetiser";
                desc = "Demagnetise component to remove residual field post-MPI.";
                opTimeSec = 36; loadUnloadSec = 0;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 17:
                machine = "Industrial Washing Machine";
                desc = "High-pressure clean bores and oil holes to remove particulate.";
                opTimeSec = 108; loadUnloadSec = 5;
                newToolCost = 200; toolLifeVal = 5000; unit = "Min"; regrinds = 1; regrindCost = 0;
                break;
            case 18:
                machine = "Manual";
                desc = "100% visual inspection check for cosmetic and handle defects.";
                opTimeSec = 90; loadUnloadSec = 0;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 19:
                machine = "Inspection Fixture";
                desc = "100% parameter inspection: Center Distance (CD), bend, and twist.";
                opTimeSec = 150; loadUnloadSec = 5;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 20:
                machine = "Laser Marker";
                desc = "Laser etch tracking barcode and part serialization.";
                opTimeSec = 42; loadUnloadSec = 5;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 21:
                machine = "Manual";
                desc = "Final inspection audit check and customer pack release.";
                opTimeSec = 90; loadUnloadSec = 0;
                newToolCost = 0; toolLifeVal = 0; regrinds = 0; regrindCost = 0;
                break;
            case 22:
                machine = "Manual";
                desc = "Apply rust preventive oil coat and pack into final container.";
                opTimeSec = 72; loadUnloadSec = 5;
                newToolCost = 250; toolLifeVal = 500; unit = "Min"; regrinds = 1; regrindCost = 0;
                break;
        }

        return {
            opIdx, name, machine,
            machineCostLakh: getMachineCostLakh(machine),
            desc, partsLoaded, cutLength, positions,
            opTimeSec, loadUnloadSec,
            newToolCost, toolLifeVal, unit, regrinds, regrindCost,
            isManual
        };
    });
}

// ── Recalculate all outputs ──
function recalculateEngine() {
    const batchSize      = Math.max(1, parseInt(document.getElementById('batchSize').value)      || 1);
    const baseHourlyRate = Math.max(0, parseFloat(document.getElementById('baseHourlyRate').value)|| 0);
    const partName       = document.getElementById('partName').value;
    const docNum         = document.getElementById('docNum').value;
    const customerName   = document.getElementById('customerName').value;
    const materialGrade  = document.getElementById('materialGrade').value;
    const hardnessValue  = document.getElementById('hardnessValue').value;

    document.getElementById('metaSummary').innerText = `${partName} | ${materialGrade} (${hardnessValue})`;

    let totalCycleTime = 0, totalCPC = 0, totalYieldSum = 0, activeOps = 0;
    const computed = [];

    operationState.forEach(op => {
        let cycleMin = 0, machCostINR = 0;
        let totalLife = 0, partsProduced = 0;
        let totalToolCost = 0, toolCostPcINR = 0, stageCpcINR = 0, shiftYield = 0;

        if (!op.isManual) {
            const parts    = Math.max(1, op.partsLoaded);
            const cycleSec = (op.opTimeSec / parts) + op.loadUnloadSec;
            cycleMin       = cycleSec / 60.0;

            // Machining cost uses the hourly rate from the sidebar
            machCostINR = (cycleMin / 60.0) * baseHourlyRate;

            // Tool Life
            if (op.unit === 'Mtr') {
                totalLife = op.toolLifeVal + (op.toolLifeVal * op.regrinds * 0.8);
                const cl  = Math.max(0.001, op.cutLength);
                const pos = Math.max(1, op.positions);
                partsProduced = Math.round((totalLife * 1000) / (cl * pos));
            } else {
                totalLife     = op.toolLifeVal * op.regrinds;
                const pos     = Math.max(1, op.positions);
                partsProduced = (cycleMin > 0) ? Math.round(totalLife / (cycleMin * pos)) : 0;
            }

            totalToolCost  = op.newToolCost + (op.regrinds * op.regrindCost);
            toolCostPcINR  = partsProduced > 0 ? (totalToolCost / partsProduced) : 0;
            stageCpcINR    = machCostINR + toolCostPcINR;
            shiftYield     = cycleMin > 0 ? Math.floor((8 * 60) / cycleMin) : 0;

            totalCycleTime += cycleMin;
            totalYieldSum  += shiftYield;
            activeOps++;
        }

        computed.push({ ...op, cycleMin, machCostINR, totalLife, partsProduced, totalToolCost, toolCostPcINR, stageCpcINR, shiftYield });
    });

    const avgYield = activeOps > 0 ? Math.round(totalYieldSum / activeOps) : 0;
    document.getElementById('kpiCycleTime').innerText = `${totalCycleTime.toFixed(2)} Mins`;
    document.getElementById('kpiYield').innerText     = `${avgYield} pcs`;

    // Update only output (read-only) cells to preserve focus on input cells
    const tbody = document.getElementById('routingTableBody');
    computed.forEach((row, i) => {
        const tr = tbody.children[i];
        if (!tr) return;
        const q = sel => tr.querySelector(sel);
        if (row.isManual) {
            q('.cycle-cell').innerText = '-';
            q('.mcost-cell').innerText = '-';
            q('.tlife-cell').innerText = '-';
            q('.pprod-cell').innerText = '-';
            q('.tcost-cell').innerText = '-';
            q('.yield-cell').innerText = '-';
        } else {
            q('.cycle-cell').innerText = row.cycleMin.toFixed(2);
            q('.mcost-cell').innerText = `₹${row.machCostINR.toFixed(2)}`;
            q('.tlife-cell').innerText = `${row.totalLife.toFixed(1)} ${row.unit}`;
            q('.pprod-cell').innerText = row.partsProduced.toLocaleString('en-IN');
            q('.tcost-cell').innerText = `₹${row.toolCostPcINR.toFixed(3)}`;
            q('.yield-cell').innerText = row.cycleMin > 0 ? row.shiftYield : '-';
        }
    });

    updateCharts(computed);
    window.routingCalculations = computed;
    window.projectMetadata = { docNum, partName, customerName, materialGrade, hardnessValue };
}

// ── Render table rows once ──
function renderTableStructure() {
    const tbody = document.getElementById('routingTableBody');
    tbody.innerHTML = '';

    operationState.forEach((op, index) => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-index', index);
        const num = String(op.opIdx).padStart(2, '0');

        if (op.isManual) {
            tr.innerHTML = `
                <td><span class="op-badge">${num}</span></td>
                <td style="font-weight:600;">${op.name}</td>
                <td class="col-machine"><input type="text" class="ti col-machine-inp" value="${op.machine}"></td>
                <td class="col-mcost"><input type="number" class="ti ti-num col-mclakh" value="${op.machineCostLakh}" min="0" step="1" placeholder="Lakh"></td>
                <td><input type="text" class="ti col-desc" value="${op.desc}"></td>
                <td style="text-align:right;color:#94a3b8;">-</td>
                <td style="text-align:right;color:#94a3b8;">-</td>
                <td style="text-align:right;color:#94a3b8;">-</td>
                <td style="text-align:right;color:#94a3b8;">-</td>
                <td style="text-align:right;color:#94a3b8;">-</td>
                <td class="cycle-cell col-cycle" style="text-align:right;">-</td>
                <td class="mcost-cell" style="text-align:right;">-</td>
                <td style="color:#94a3b8;">-</td><td style="color:#94a3b8;">-</td><td style="color:#94a3b8;">-</td>
                <td style="color:#94a3b8;">-</td><td style="color:#94a3b8;">-</td>
                <td class="tlife-cell" style="text-align:right;">-</td>
                <td class="pprod-cell" style="text-align:right;">-</td>
                <td class="tcost-cell" style="text-align:right;">-</td>
                <td class="yield-cell" style="text-align:right;display:none;">-</td>`;
        } else {
            tr.innerHTML = `
                <td><span class="op-badge">${num}</span></td>
                <td style="font-weight:600;">${op.name}</td>
                <!-- Machine group -->
                <td class="col-machine"><input type="text" class="ti col-machine-inp" value="${op.machine}"></td>
                <td class="col-mcost"><input type="number" class="ti ti-num col-mclakh" value="${op.machineCostLakh}" min="0" step="1" placeholder="Lakh"></td>
                <!-- Process & sizing inputs -->
                <td><input type="text" class="ti col-desc" value="${op.desc}" style="min-width:160px;"></td>
                <td><input type="number" class="ti ti-num col-parts" value="${op.partsLoaded}" min="1"></td>
                <td><input type="number" class="ti ti-num col-cutlen" value="${op.cutLength}" min="0"></td>
                <td><input type="number" class="ti ti-num col-positions" value="${op.positions}" min="1"></td>
                <td><input type="number" class="ti ti-num col-optime" value="${op.opTimeSec}" min="0"></td>
                <td><input type="number" class="ti ti-num col-loadtime" value="${op.loadUnloadSec}" min="0"></td>
                <!-- Calculated cycle outputs -->
                <td class="cycle-cell col-cycle" style="text-align:right;font-weight:700;">0.00</td>
                <td class="mcost-cell" style="text-align:right;">₹0.00</td>
                <!-- Tooling inputs -->
                <td><input type="number" class="ti ti-num col-newcost" value="${op.newToolCost}" min="0"></td>
                <td><input type="number" class="ti ti-num col-lifeval" value="${op.toolLifeVal}" min="0"></td>
                <td>
                    <select class="ti-sel col-unit">
                        <option value="Mtr" ${op.unit==='Mtr'?'selected':''}>Mtr</option>
                        <option value="Min" ${op.unit==='Min'?'selected':''}>Min</option>
                    </select>
                </td>
                <td><input type="number" class="ti ti-num col-regrinds" value="${op.regrinds}" min="0"></td>
                <td><input type="number" class="ti ti-num col-regrindcost" value="${op.regrindCost}" min="0"></td>
                <!-- Tooling outputs -->
                <td class="tlife-cell" style="text-align:right;">0.0</td>
                <td class="pprod-cell" style="text-align:right;">0</td>
                <td class="tcost-cell" style="text-align:right;">₹0.000</td>
                <td class="yield-cell" style="display:none;">0</td>`;
        }

        tbody.appendChild(tr);
    });

    // Single delegated listener on tbody
    tbody.addEventListener('input', handleTableInput);
    tbody.addEventListener('change', handleTableInput);
}

function handleTableInput(e) {
    const tr  = e.target.closest('tr');
    if (!tr) return;
    const idx = parseInt(tr.getAttribute('data-index'));
    const op  = operationState[idx];
    const cl  = e.target.classList;

    if (cl.contains('col-machine-inp'))  op.machine          = e.target.value;
    if (cl.contains('col-mclakh'))       op.machineCostLakh  = Math.max(0, parseFloat(e.target.value) || 0);
    if (cl.contains('col-desc'))         op.desc             = e.target.value;
    if (cl.contains('col-parts'))        op.partsLoaded      = Math.max(1, parseInt(e.target.value)   || 1);
    if (cl.contains('col-cutlen'))       op.cutLength        = Math.max(0, parseFloat(e.target.value) || 0);
    if (cl.contains('col-positions'))    op.positions        = Math.max(1, parseInt(e.target.value)   || 1);
    if (cl.contains('col-optime'))       op.opTimeSec        = Math.max(0, parseInt(e.target.value)   || 0);
    if (cl.contains('col-loadtime'))     op.loadUnloadSec    = Math.max(0, parseInt(e.target.value)   || 0);
    if (cl.contains('col-newcost'))      op.newToolCost      = Math.max(0, parseFloat(e.target.value) || 0);
    if (cl.contains('col-lifeval'))      op.toolLifeVal      = Math.max(0, parseFloat(e.target.value) || 0);
    if (cl.contains('col-unit'))         op.unit             = e.target.value;
    if (cl.contains('col-regrinds'))     op.regrinds         = Math.max(0, parseInt(e.target.value)   || 0);
    if (cl.contains('col-regrindcost'))  op.regrindCost      = Math.max(0, parseFloat(e.target.value) || 0);

    recalculateEngine();
}

function updateCharts(data) {
    const maxCycle = Math.max(...data.map(r => r.cycleMin), 1);
    const maxCpc   = Math.max(...data.map(r => r.stageCpcINR), 0.1);

    ['cycleTimeChartList', 'costChartList'].forEach(id => document.getElementById(id).innerHTML = '');

    data.forEach(row => {
        if (row.cycleMin <= 0) return;

        const makeRow = (pct, val, fillClass) => {
            const d = document.createElement('div');
            d.className = 'bar-chart-row';
            d.innerHTML = `
                <span class="bar-chart-label" title="${row.name}">${row.name}</span>
                <div class="bar-chart-container">
                    <div class="bar-chart-fill ${fillClass}" style="width:${pct}%"></div>
                </div>
                <span class="bar-chart-value">${val}</span>`;
            return d;
        };

        document.getElementById('cycleTimeChartList')
            .appendChild(makeRow((row.cycleMin / maxCycle) * 100, `${row.cycleMin.toFixed(2)}m`, ''));

        document.getElementById('costChartList')
            .appendChild(makeRow((row.stageCpcINR / maxCpc) * 100, `₹${row.stageCpcINR.toFixed(2)}`, 'chart-cpc-fill'));
    });
}

// ── Init ──
function initialize() {
    buildInitialState();
    renderTableStructure();
    recalculateEngine();
}

// Sidebar changes → full rebuild
document.querySelectorAll('.form-control').forEach(inp => {
    inp.addEventListener('change', () => {
        buildInitialState();
        renderTableStructure();
        recalculateEngine();
    });
});

// CSV Download
document.getElementById('downloadCsvBtn').addEventListener('click', () => {
    if (!window.routingCalculations) return;
    const meta = window.projectMetadata;
    let csv = `data:text/csv;charset=utf-8,`;
    csv += `Document Number,${meta.docNum}\nPart Name,${meta.partName}\nCustomer Name,${meta.customerName}\nMaterial,${meta.materialGrade}\nHardness,${meta.hardnessValue}\n\n`;
    csv += `Op #,Operation Name,Machine,Machine Cost (Lakh INR),Process Description,Parts Loaded,Cut Length (mm),Positions,Op Time (Sec),Load/Unload (Sec),Cycle (Min),Mach. Cost (INR/pc),New Tool Cost (INR),Tool Life,Unit,Regrinds,Regrind Cost (INR),Total Life,Parts Produced,Tool Cost (INR/pc)\n`;

    window.routingCalculations.forEach(row => {
        const d = row.desc.replace(/"/g, '""');
        const dash = (v) => row.isManual ? '-' : v;
        csv += `"${row.opIdx}","${row.name}","${row.machine}","${dash(row.machineCostLakh)}","${d}",${dash(row.partsLoaded)},${dash(row.cutLength)},${dash(row.positions)},${dash(row.opTimeSec)},${dash(row.loadUnloadSec)},${dash(row.cycleMin.toFixed(2))},${dash(row.machCostINR.toFixed(2))},${dash(row.newToolCost)},${dash(row.toolLifeVal)},"${dash(row.unit)}",${dash(row.regrinds)},${dash(row.regrindCost)},${dash(row.totalLife.toFixed(1))},${dash(row.partsProduced)},${dash(row.toolCostPcINR.toFixed(3))}\n`;
    });

    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csv));
    link.setAttribute('download', `routing_card_${meta.docNum}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

window.addEventListener('DOMContentLoaded', initialize);
</script>
</body>
</html>
