"""Week 4 step 1: Larkspur CENTRAL projection (no climate event), FY2027-FY2028 by quarter.

CDA step: baseline for step 4 (enterprise consequences). Every scenario in Week 4 is a departure from this.

Sources (client records, never edited; paths under client data/windward-risk-advisors/clients/larkspur-foods/):
  data/division-pnl.csv              FY2024-25 revenue and EBITDA by division, FY2025 capex
  data/beverage-volume-by-line.csv   FY2025 cases and revenue by Beverage line and production site
  reference.md                       FY2025 contribution margin by Beverage line (typed in below)
  board-minutes-excerpt.md           March 2027 functional-line launch, $18.5M slotting and launch marketing
  credit-agreement-excerpt.md        net debt build-up, 3.50x springing covenant, revolver peak $138.0M, maturities
  copacker-agreement-excerpt.md      Gonzales rated capacity 19.0M cases, 15.0M minimum commitment
  logistics-note.md                  27 days Beverage finished goods, 14 staged at Gonzales; FY2027 berry volume +40%

Run:  ~/.venvs/kith-climate/bin/python scenarios/build_central_projection.py   (from 3 Larkspur/)
Writes scenarios/central-projection.json and scenarios/central-projection.md. Touches nothing else.
Labels: RECORD (from the pack), MODEL (calculated here), ASSUMPTION (ours, to confirm).
"""
import csv, hashlib, json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACK = ROOT / "client data/windward-risk-advisors/clients/larkspur-foods"
OUT_JSON = ROOT / "scenarios/central-projection.json"
OUT_MD = ROOT / "scenarios/central-projection.md"
RUN_ID = "P-20261009-01"
INPUTS = ["data/division-pnl.csv", "data/beverage-volume-by-line.csv", "reference.md", "board-minutes-excerpt.md",
          "credit-agreement-excerpt.md", "copacker-agreement-excerpt.md", "logistics-note.md"]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def read_csv(name):
    with open(PACK / name) as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))

# ---------------------------------------------------------------- RECORDS
div = {r["division"]: r for r in read_csv("data/division-pnl.csv")}
bev = read_csv("data/beverage-volume-by-line.csv")
CM = {"BV-01": .30, "BV-02": .28, "BV-03": .26, "BV-04": .29, "BV-05": .38, "BV-06": .14, "BV-07": .35}  # reference.md, Beverage line detail
REC = dict(
    rated_capacity_k=19000.0, min_commit_k=15000.0,            # copacker Art. 3.1-3.2
    fg_days=27, staged_days=14,                                # logistics note
    launch_cost=18.5,                                          # board minutes item 5
    tlb=900.0, revolver=45.0, leases=18.0, cash=129.0, net_debt=834.0, covenant=3.50,  # credit agreement certificate
    revolver_peak=138.0, revolver_commit=250.0, test_trigger=0.35, lcs=12.0,
    berry_uplift=0.40,                                         # logistics note, FY2027 planning items
)
for l in bev:
    l["cases"], l["rev"] = float(l["annual_cases_k"]), float(l["fy2025_revenue_usd_m"])
    l["gonz"] = l["production_site"].startswith("Gonzales")

# ---------------------------------------------------------------- ASSUMPTIONS (ours)
A = dict(
    price=0.02,              # price/mix per year, all Beverage lines
    vol_other=0.02,          # San Antonio and Holland lines, volume per year
    vol_gonz_core=0.0,       # BV-03, BV-04, BV-06 volume per year (lines are 95% full)
    func_fy26_k=2100.0,      # functional line flat until launch
    func_fy27_q=[615.0, 775.0, 775.0, 775.0],   # launch 1 Mar 2027: +40% on FY2025 for the year, exit run-rate 775k/quarter
    func_fy28_q=[775.0] * 4,
    fixed_growth=0.03,       # Beverage fixed cost per year
    gonz_fixed_share=312.0 / 520.0,  # fixed cost split by FY2025 revenue
    launch_phasing=[0.60, 0.25, 0.15, 0.0],
    ing_growth=1300.0 / 1245.0 - 1, pro_growth=680.0 / 655.0 - 1,  # FY2025 growth repeated
    corp_growth=0.03,
    capex=75.0, da=75.0, rate=0.07, tax=0.25, dividends=20.0, nwc_pct=0.12,
    peak_build=REC["revolver_peak"] - REC["revolver"],   # FY2025 revolver swing repeated at the October test
)

Q = ["Q1", "Q2", "Q3", "Q4"]
QP = [f"FY{y} {q}" for y in (2027, 2028) for q in Q]
PERIODS = ["FY2025", "FY2026"] + QP + ["FY2027", "FY2028"]
QDAYS, YDAYS = 91, 364   # 52-week fiscal year ending late December (FY2025 ended 27 Dec 2025)

def cell(v, l, d=2):
    return {"v": None if v is None else round(v, d), "l": l}

# ---------------------------------------------------------------- Beverage by line and period
def line_cases(l, period):
    yr = int(period[2:6]); q = period[-2:] if " " in period else None
    if yr == 2025: return l["cases"]
    n = yr - 2025
    if l["line_id"] == "BV-05":
        if yr == 2026: return A["func_fy26_k"]
        qs = A["func_fy27_q"] if yr == 2027 else A["func_fy28_q"]
        return qs[Q.index(q)] if q else sum(qs)
    g = A["vol_gonz_core"] if l["gonz"] else A["vol_other"]
    annual = l["cases"] * (1 + g) ** n
    return annual / 4 if q else annual

def line_rev(l, period):
    n = int(period[2:6]) - 2025
    return line_cases(l, period) * (l["rev"] / l["cases"]) * (1 + A["price"]) ** n

def fixed_total(period):
    yr = int(period[2:6]); q = period[-2:] if " " in period else None
    base = (sum(l["rev"] * CM[l["line_id"]] for l in bev) - float(div["Beverage"]["fy2025_ebitda_usd_m"])) * (1 + A["fixed_growth"]) ** (yr - 2025)
    launch = REC["launch_cost"] * (A["launch_phasing"][Q.index(q)] if q else 1.0) if yr == 2027 else 0.0
    return (base / 4 if q else base), launch

def bev_block(period):
    out = {}
    for grp, sel in (("gonzales", lambda l: l["gonz"]), ("other_lines", lambda l: not l["gonz"])):
        ls = [l for l in bev if sel(l)]
        cases = sum(line_cases(l, period) for l in ls)
        rev = sum(line_rev(l, period) for l in ls)
        var = sum(line_rev(l, period) * (1 - CM[l["line_id"]]) for l in ls)
        base, launch = fixed_total(period)
        share = A["gonz_fixed_share"] if grp == "gonzales" else 1 - A["gonz_fixed_share"]
        fixed = base * share + (launch if grp == "gonzales" else 0.0)
        days = QDAYS if " " in period else YDAYS
        out[grp] = dict(cases_k=cases, revenue=rev, variable_cost=var, contribution=rev - var, fixed_cost=fixed,
                        of_which_launch=launch if grp == "gonzales" else 0.0, ebitda=rev - var - fixed,
                        fg_inventory_cases_k=cases / days * REC["fg_days"], fg_inventory_usd=var / days * REC["fg_days"])
        if grp == "gonzales":
            out[grp]["fg_staged_at_gonzales_cases_k"] = cases / days * REC["staged_days"]
            cap = REC["rated_capacity_k"] / (4 if " " in period else 1)
            out[grp]["capacity_k"] = cap
            out[grp]["utilisation_pct"] = 100 * cases / cap
            out[grp]["spare_capacity_k"] = cap - cases
    out["total"] = {k: out["gonzales"][k] + out["other_lines"][k] for k in out["other_lines"]}
    return out

B = {p: bev_block(p) for p in PERIODS}

# ---------------------------------------------------------------- Larkspur-wide EBITDA
def company(period):
    yr = int(period[2:6]); n = yr - 2025; f = 0.25 if " " in period else 1.0
    ing_rev = 1300.0 * (1 + A["ing_growth"]) ** n * f
    pro_rev = 680.0 * (1 + A["pro_growth"]) ** n * f
    ing = ing_rev * 208.0 / 1300.0
    pro = pro_rev * 47.6 / 680.0
    corp = -25.5 * (1 + A["corp_growth"]) ** n * f
    bv = B[period]["total"]
    return dict(ingredients_revenue=ing_rev, produce_revenue=pro_rev, beverage_revenue=bv["revenue"],
                revenue=ing_rev + pro_rev + bv["revenue"], ingredients_ebitda=ing, produce_ebitda=pro,
                beverage_ebitda=bv["ebitda"], corporate=corp, ebitda=ing + pro + bv["ebitda"] + corp)

C = {p: company(p) for p in PERIODS}

# ---------------------------------------------------------------- Net debt and leverage
def cash_flow(ebitda, rev_change, opening_nd, f):
    interest = A["rate"] * (opening_nd + REC["cash"]) * f          # gross debt = net debt + cash held at the FY2025 level
    tax = max(0.0, A["tax"] * (ebitda - A["da"] * f - interest))
    nwc = A["nwc_pct"] * rev_change
    fcf = ebitda - A["capex"] * f - interest - tax - A["dividends"] * f - nwc
    return dict(capex=A["capex"] * f, interest=interest, tax=tax, dividends=A["dividends"] * f, nwc_increase=nwc, fcf=fcf)

CF, ND = {}, {"FY2025": REC["net_debt"]}
CF["FY2026"] = cash_flow(C["FY2026"]["ebitda"], C["FY2026"]["revenue"] - C["FY2025"]["revenue"], REC["net_debt"], 1.0)
ND["FY2026"] = REC["net_debt"] - CF["FY2026"]["fcf"]
prev = "FY2026"
for p in QP:
    yr = int(p[2:6])
    rev_change = (C[f"FY{yr}"]["revenue"] - C[f"FY{yr-1}"]["revenue"]) / 4
    CF[p] = cash_flow(C[p]["ebitda"], rev_change, ND[prev], 0.25)
    ND[p] = ND[prev] - CF[p]["fcf"]
    prev = p
for yr in (2027, 2028):
    ps = [f"FY{yr} {q}" for q in Q]
    CF[f"FY{yr}"] = {k: sum(CF[p][k] for p in ps) for k in CF[ps[0]]}
    ND[f"FY{yr}"] = ND[ps[-1]]

def ltm(p):
    if p in ("FY2025", "FY2026", "FY2027", "FY2028"): return C[p]["ebitda"]
    yr, i = int(p[2:6]), Q.index(p[-2:])
    seq = [C["FY2026"]["ebitda"] / 4] * 4 + [C[f"FY2027 {q}"]["ebitda"] for q in Q] + [C[f"FY2028 {q}"]["ebitda"] for q in Q]
    end = 4 * (yr - 2026) + i + 1
    return sum(seq[end - 4:end])

LEV = {p: dict(net_debt=ND[p], ltm_ebitda=ltm(p), leverage=ND[p] / ltm(p),
               headroom=ltm(p) - ND[p] / REC["covenant"]) for p in PERIODS}

# October test: Q3-end net debt plus the harvest build, against LTM EBITDA at Q3
OCT = {}
for yr in (2025, 2027, 2028):
    if yr == 2025:
        nd0, e = REC["net_debt"], C["FY2025"]["ebitda"]   # illustrative: year-end net debt plus the recorded swing
    else:
        nd0, e = ND[f"FY{yr} Q3"], ltm(f"FY{yr} Q3")
    nd = nd0 + A["peak_build"]
    draw = REC["revolver"] + A["peak_build"] if yr == 2025 else None
    OCT[f"Oct {yr}"] = dict(net_debt_before_build=nd0, harvest_build=A["peak_build"], net_debt_at_test=nd, ltm_ebitda=e,
                            leverage=nd / e, headroom=e - nd / REC["covenant"], ebitda_at_3_5x=nd / REC["covenant"])

# ---------------------------------------------------------------- Reconciliation to the pack (FY2025)
bev25 = B["FY2025"]
recon = [
    ("Beverage revenue, sum of seven lines", 520.0, bev25["total"]["revenue"], "division-pnl.csv Beverage fy2025_revenue_usd_m"),
    ("Gonzales lines revenue (BV-03 to BV-06)", 312.0, bev25["gonzales"]["revenue"], "Week 3 run R-20261001-02 records.gonzales_rev"),
    ("Gonzales lines contribution", 86.76, bev25["gonzales"]["contribution"], "Week 3 run R-20261001-02 records.gonzales_contrib"),
    ("Gonzales cases, thousand", 18000.0, bev25["gonzales"]["cases_k"], "beverage-volume-by-line.csv; 95% of 19.0M rated"),
    ("Beverage EBITDA", 67.6, bev25["total"]["ebitda"], "division-pnl.csv (holds by construction: fixed cost is the balancing figure)"),
    ("Larkspur revenue", 2500.0, C["FY2025"]["revenue"], "division-pnl.csv Total"),
    ("Larkspur adjusted EBITDA", 297.7, C["FY2025"]["ebitda"], "division-pnl.csv Total; compliance certificate"),
    ("Net debt: 900 + 45 + 18 - 129", 834.0, REC["tlb"] + REC["revolver"] + REC["leases"] - REC["cash"], "credit agreement certificate"),
    ("First-lien net leverage", 2.8, REC["net_debt"] / C["FY2025"]["ebitda"], "credit agreement certificate (2.8x)"),
    ("Headroom to 3.50x at year-end net debt", 59.4, LEV["FY2025"]["headroom"], "Week 3 scenario-set.json dependency facts"),
]
RECON = [dict(item=i, pack=p, model=round(m, 2), ok=abs(m - p) < 0.05, src=s) for i, p, m, s in recon]
assert all(r["ok"] for r in RECON), RECON

# ---------------------------------------------------------------- Second-way check (closed-form annual arithmetic, independent of the period functions)
pi27, pi28 = 1.02 ** 2, 1.02 ** 3
rpc = {l["line_id"]: l["rev"] / l["cases"] for l in bev}
core = ["BV-03", "BV-04", "BV-06"]; other = ["BV-01", "BV-02", "BV-07"]
chk_g27 = sum(next(l["cases"] for l in bev if l["line_id"] == k) * rpc[k] for k in core) * pi27 + 2940 * rpc["BV-05"] * pi27
chk_o27 = sum(next(l["cases"] for l in bev if l["line_id"] == k) * rpc[k] for k in other) * 1.02 ** 2 * pi27
chk_fixed27 = 81.21 * 1.03 ** 2 + 18.5
cm_g = sum(next(l["cases"] for l in bev if l["line_id"] == k) * rpc[k] * CM[k] for k in core) * pi27 + 2940 * rpc["BV-05"] * pi27 * CM["BV-05"]
cm_o = sum(next(l["cases"] for l in bev if l["line_id"] == k) * rpc[k] * CM[k] for k in other) * 1.02 ** 2 * pi27
chk_bev_e27 = cm_g + cm_o - chk_fixed27
CHECK = [
    dict(item="FY2027 Gonzales revenue", main=B["FY2027"]["gonzales"]["revenue"], check=chk_g27),
    dict(item="FY2027 other-lines revenue", main=B["FY2027"]["other_lines"]["revenue"], check=chk_o27),
    dict(item="FY2027 Beverage EBITDA", main=B["FY2027"]["total"]["ebitda"], check=chk_bev_e27),
    dict(item="FY2027 Gonzales utilisation %", main=B["FY2027"]["gonzales"]["utilisation_pct"], check=100 * (15900 + 2940) / 19000),
    dict(item="FY2028 Gonzales utilisation %", main=B["FY2028"]["gonzales"]["utilisation_pct"], check=100 * (15900 + 3100) / 19000),
]
for c in CHECK:
    c["main"], c["check"] = round(c["main"], 3), round(c["check"], 3)
    c["agree"] = abs(c["main"] - c["check"]) < 0.01
assert all(c["agree"] for c in CHECK), CHECK

# ---------------------------------------------------------------- Sensitivities (each changes one assumption, MODEL)
def gonz_demand_k(core_growth, func_k):
    return 15900 * (1 + core_growth) ** 3 + func_k
over = gonz_demand_k(0.02, 3100) - REC["rated_capacity_k"]
func_cm_per_k = rpc["BV-05"] * 1.02 ** 3 * CM["BV-05"]
SENS = [
    dict(change="Gonzales core lines (BV-03, -04, -06) grow volume 2% a year instead of flat",
         effect=f"FY2028 Gonzales demand {gonz_demand_k(0.02, 3100)/1000:.2f}M cases against 19.0M rated: {over/1000:.2f}M cases a year cannot be filled. "
                f"'Capacity meets demand' fails from FY2027.", label="MODEL"),
    dict(change="Launch reaches half the volume (+20% on FY2025, not +40%)",
         effect=f"Functional line about 420k cases a year lower; Beverage EBITDA about ${420*func_cm_per_k:.1f}M a year lower in FY2028; Gonzales keeps ~0.6M cases of spare capacity.",
         label="MODEL"),
    dict(change="Beverage price/mix +1% a year instead of +2%",
         effect=f"FY2028 Beverage EBITDA about ${B['FY2028']['total']['revenue'] * (1 - 1.01**3/1.02**3) * (B['FY2028']['total']['contribution']/B['FY2028']['total']['revenue']):.1f}M lower (margin held).",
         label="MODEL"),
    dict(change="Dividends $40M a year instead of $20M, or interest at 8% instead of 7%",
         effect=f"Each adds roughly $20M and $7M (before tax) a year respectively to net debt; FY2028 year-end leverage moves by about 0.1x and 0.04x.", label="MODEL"),
]

# ---------------------------------------------------------------- Assemble JSON
L = lambda p: "RECORD" if p == "FY2025" else "MODEL"
def rows(src, keys, names, units, fy25_labels=None):
    out = []
    for k, n, u in zip(keys, names, units):
        out.append(dict(key=k, name=n, unit=u,
                        values={p: cell(src(p)[k], (fy25_labels or {}).get(k, L(p)) if p == "FY2025" else "MODEL") for p in PERIODS}))
    return out

BKEYS = ["cases_k", "revenue", "variable_cost", "contribution", "fixed_cost", "of_which_launch", "ebitda", "fg_inventory_cases_k", "fg_inventory_usd"]
BNAMES = ["Cases sold", "Revenue", "Variable cost", "Contribution", "Fixed cost", "of which launch slotting and marketing", "EBITDA",
          "Finished goods on hand (27 days)", "Finished goods on hand at variable cost"]
BUNITS = ["thousand cases", "$M", "$M", "$M", "$M", "$M", "$M", "thousand cases", "$M"]
# FY2025 labels: revenue and cases are records; variable cost uses recorded margins (MODEL); fixed cost is the balancing figure (MODEL)
FY25L = dict(cases_k="RECORD", revenue="RECORD", variable_cost="MODEL", contribution="MODEL", fixed_cost="MODEL",
             of_which_launch="RECORD", ebitda="MODEL", fg_inventory_cases_k="MODEL", fg_inventory_usd="MODEL",
             fg_staged_at_gonzales_cases_k="MODEL", capacity_k="RECORD", utilisation_pct="MODEL", spare_capacity_k="MODEL")
FY25L_TOT = dict(FY25L, ebitda="RECORD")

beverage = {
    "gonzales": rows(lambda p: B[p]["gonzales"], BKEYS + ["fg_staged_at_gonzales_cases_k", "capacity_k", "utilisation_pct", "spare_capacity_k"],
                     BNAMES + ["of which staged at Gonzales (14 days)", "Rated capacity, Lines 2 and 3", "Utilisation", "Spare capacity"],
                     BUNITS + ["thousand cases", "thousand cases", "%", "thousand cases"], FY25L),
    "other_lines": rows(lambda p: B[p]["other_lines"], BKEYS, BNAMES, BUNITS, FY25L),
    "total": rows(lambda p: B[p]["total"], BKEYS, BNAMES, BUNITS, FY25L_TOT),
}
for grp in ("gonzales", "other_lines", "total"):
    for r in beverage[grp]:
        if r["key"] == "capacity_k":
            for p in PERIODS: r["values"][p]["l"] = "RECORD"
CKEYS = ["ingredients_revenue", "produce_revenue", "beverage_revenue", "revenue", "ingredients_ebitda", "produce_ebitda", "beverage_ebitda", "corporate", "ebitda"]
company_rows = rows(lambda p: C[p], CKEYS,
                    ["Ingredients revenue", "Produce revenue", "Beverage revenue", "Larkspur revenue", "Ingredients EBITDA", "Produce EBITDA",
                     "Beverage EBITDA", "Corporate and unallocated", "Larkspur adjusted EBITDA"], ["$M"] * 9,
                    {k: "RECORD" for k in CKEYS})
debt_rows = []
for k, n, u in [("net_debt", "Net debt, period end", "$M"), ("ltm_ebitda", "EBITDA, last twelve months", "$M"),
                ("leverage", "First-lien net leverage", "x"), ("headroom", "EBITDA headroom before 3.50x", "$M")]:
    debt_rows.append(dict(key=k, name=n, unit=u, values={p: cell(LEV[p][k], ("RECORD" if k != "headroom" else "MODEL") if p == "FY2025" else "MODEL")
                                                          for p in PERIODS}))
cash_periods = ["FY2026"] + QP + ["FY2027", "FY2028"]
cash_rows = [dict(key=k, name=n, unit="$M", values={p: cell(CF[p][k], "MODEL") for p in cash_periods})
             for k, n in [("capex", "Capital expenditure"), ("interest", "Cash interest"), ("tax", "Cash tax"), ("dividends", "Dividends"),
                          ("nwc_increase", "Working-capital build"), ("fcf", "Free cash flow to debt")]]

ASSUME = [
    dict(id="price", value="+2.0% a year price/mix on every Beverage line", range="0% to +4%", why="FY2025 Beverage revenue grew 6.1% (RECORD); the price/volume split is not in the pack", who="President, Beverage"),
    dict(id="vol_other", value="+2.0% a year volume at San Antonio and Holland", range="0% to +4%", why="San Antonio capacity is not in the pack and the Line 3 expansion is deferred (board minutes item 4)", who="COO"),
    dict(id="vol_gonz_core", value="Flat volume on BV-03, BV-04, BV-06 (15.9M cases)", range="0% to +2%", why="Lines 2 and 3 run at 95%; with the launch, any core growth exceeds rated capacity (see sensitivity 1)", who="COO; President, Beverage"),
    dict(id="launch", value="Functional line (BV-05) launches 1 March 2027: 2,940k cases in FY2027 (+40% on FY2025), 3,100k in FY2028 (775k a quarter)", range="+20% to +50%",
         why="Sized on the +40% berry procurement for FY2027 (logistics note, RECORD); the volume plan itself is missing", who="President, Beverage"),
    dict(id="margins", value="FY2025 contribution margin by line held constant", range="±2 points", why="Price assumed to pass through cost inflation; carton and resin pass through at cost +2% (co-pack schedules)", who="CFO"),
    dict(id="fixed", value="Beverage fixed cost $81.2M in FY2025 (balancing figure), +3% a year; 60% allocated to Gonzales lines by revenue", range="+2% to +4%; allocation does not change Beverage or Larkspur EBITDA",
         why="The pack has no fixed/variable split; contribution margins define variable cost", who="CFO"),
    dict(id="launch_cost", value="$18.5M slotting and launch marketing (RECORD) is incremental to run-rate cost, all in FY2027, phased 60/25/15/0 by quarter, charged to Gonzales lines", range="Phasing only", why="Board approved it within the FY2027 plan; timing not stated", who="President, Beverage"),
    dict(id="seasonality", value="Demand, costs and cash flow flat across quarters", range="", why="Same as the Week 3 model; quarterly phasing not in the pack", who="CFO"),
    dict(id="fg", value="Beverage finished goods held at 27 days of sales, 14 staged at Gonzales, valued at variable cost", range="", why="Days are RECORD (logistics note); valuation basis is not in the pack", who="Logistics; Controller"),
    dict(id="other_divisions", value="Ingredients +4.4% and Produce +3.8% revenue a year (FY2025 growth repeated), FY2025 margins held; corporate cost +3%", range="", why="No plan figures in the pack", who="CFO"),
    dict(id="fy2026", value="FY2026 built with the same rules (functional line flat); no FY2026 actuals are in the pack", range="", why="Bridge year to FY2027", who="CFO"),
    dict(id="cash", value="Capex $75M a year; D&A $75M; interest 7.0% on gross debt (net debt + $129M cash held); tax 25% of EBITDA less D&A and interest; dividends $20M; working capital 12% of revenue growth", range="See sensitivity 4",
         why="Capex is FY2025 division capex $73M (RECORD) rounded up for ERP phase 2; the rest is not in the pack", who="Treasurer; CFO"),
    dict(id="refinance", value="Revolver (matures Dec 2027) and Term Loan B (bullet June 2028) refinanced on current terms, no fees", range="", why="Both maturities fall inside the projection; the pack has no refinancing plan", who="Treasurer"),
    dict(id="peak_build", value="Net debt rises $93.0M from Q3-end to the mid-October test, as the FY2025 revolver swing ($45M to $138M peak) did", range="$60M to $120M",
         why="Peak usage is RECORD for FY2025 only", who="Treasurer"),
    dict(id="test_springs", value="The covenant is treated as tested every October", range="", why="FY2025 peak draw of $138M was 55% of the $250M revolver, above the 35% trigger; if free cash repays the revolver first, the test may not spring", who="Treasurer"),
]
MISSING = [
    "FY2026 year-to-date actuals and the FY2027 plan (revenue, EBITDA, volume by line)",
    "Functional-line launch volume plan and slotting date (Week 3 gap, still open)",
    "Fixed and variable cost split for Beverage; finished-goods valuation basis",
    "San Antonio capacity and utilisation",
    "Interest rate actually paid (SOFR and swaps), cash tax, dividend amount, D&A",
    "Quarterly seasonality of revenue, EBITDA and working capital",
    "Refinancing plan for the December 2027 revolver and June 2028 term loan",
    "How the October covenant test measures net debt (point in time, quarter-end, or average)",
]
FLAGS = [
    "Capacity: the central case only holds 'capacity meets demand' because we held Gonzales core volume flat. With the launch at +40%, Lines 2 and 3 run at 99.2% in FY2027 and 100% from Q2 FY2027 on. "
    "Spare capacity, the thing that rebuilt the buffer in the Week 3 run (1.0M cases a year), is gone in the central case. Every Week 4 scenario will recover more slowly than Week 3 showed.",
    f"Covenant headroom at the October test is smaller than the $59.4M Week 3 used. Week 3 measured headroom at year-end net debt; the test falls at the revolver peak. "
    f"Adding the FY2025 swing ($93M) gives {OCT['Oct 2025']['leverage']:.2f}x and ${OCT['Oct 2025']['headroom']:.1f}M of headroom for October 2025 (illustrative). "
    "This changes how close a scenario comes to breach. Week 3 files not edited; needs Tripp's call and the Treasurer's confirmation of the test mechanics.",
    "Both credit facilities mature inside the window (revolver Dec 2027, term loan June 2028). The central case assumes routine refinancing; a climate loss landing in 2027 lands during that refinancing.",
    "The $18.5M launch spend takes FY2027 Beverage EBITDA down even in the central case. Q1 FY2027 is the weakest quarter before any event.",
    "Several assumptions move annual EBITDA by more than $5M (price/mix, launch volume, fixed-cost growth). Per cda-workflow.md these need Tripp's review before results are quoted.",
]

SENTENCES = [
    "Lakemont, Fairmount, Callahan and every other customer keep ordering at FY2025 patterns, with Beverage prices up 2% a year and no listing lost.",
    "River Parish Aseptic Packaging fills Lines 2 and 3 every week with no force-majeure stop, and San Antonio and Holland run without interruption.",
    "The March 2027 Prairie Clover functional-line launch goes ahead on 1 March as the board approved, spending the $18.5M and lifting the functional line about 40%, in step with the berry plan.",
    "Capacity meets demand, but only because core Gonzales volumes stay flat: with the launch the lines are 99% full in FY2027 and full in FY2028, so 27 days of finished goods is held and no sale is lost.",
    "Customers pay on terms and working capital grows in line with sales, so free cash flow pays down net debt every quarter and both credit facilities are refinanced on current terms as they mature.",
    "The October revolver peak repeats the FY2025 swing, so the covenant is tested each October against net debt about $93M above the quarter-end figure.",
]

pf = lambda p: f"{LEV[p]['leverage']:.2f}x"
summary = dict(
    beverage_ebitda={p: round(B[p]["total"]["ebitda"], 1) for p in ("FY2025", "FY2026", "FY2027", "FY2028")},
    gonzales_ebitda={p: round(B[p]["gonzales"]["ebitda"], 1) for p in ("FY2025", "FY2026", "FY2027", "FY2028")},
    larkspur_ebitda={p: round(C[p]["ebitda"], 1) for p in ("FY2025", "FY2026", "FY2027", "FY2028")},
    net_debt_year_end={p: round(ND[p], 1) for p in ("FY2025", "FY2026", "FY2027", "FY2028")},
    leverage_year_end={p: round(LEV[p]["leverage"], 2) for p in ("FY2025", "FY2026", "FY2027", "FY2028")},
    october_test={k: dict(leverage=round(v["leverage"], 2), headroom=round(v["headroom"], 1)) for k, v in OCT.items()},
    label="MODEL (FY2025 figures RECORD)",
)

doc = {
    "_about": "Week 4 step 1: Larkspur CENTRAL projection, no climate event. Baseline that every Week 4 scenario departs from. Built by scenarios/build_central_projection.py; edit assumptions there and re-run. Labels: RECORD (pack), MODEL (calculated), ASSUMPTION (ours). Every number is a {v, l} pair.",
    "run": dict(run_id=RUN_ID, run_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), cda_step="4 (baseline before scenarios)",
                script="scenarios/build_central_projection.py", script_sha256=sha(pathlib.Path(__file__)),
                command="~/.venvs/kith-climate/bin/python scenarios/build_central_projection.py", inputs={f: sha(PACK / f) for f in INPUTS},
                note="Not appended to scenarios/runs/run-log.csv, to leave the Week 3 files untouched."),
    "what_it_assumes": SENTENCES,
    "periods": PERIODS,
    "period_note": "52-week fiscal year ending late December (FY2025 ended 27 December 2025). Q1 is roughly January to March. FY2025 is the pack; FY2026 is a bridge estimate; FY2027-28 are quarterly.",
    "summary": summary,
    "reconciliation_fy2025": RECON,
    "beverage": beverage,
    "larkspur": dict(ebitda=company_rows, debt=debt_rows, cash_flow=cash_rows,
                     october_test={k: {kk: cell(vv, "MODEL") for kk, vv in v.items()} for k, v in OCT.items()},
                     october_test_note="Net debt at the mid-October test = Q3-end net debt + $93.0M harvest build (ASSUMPTION from FY2025 RECORD); leverage against LTM EBITDA at Q3. Oct 2025 is illustrative: year-end net debt plus the swing."),
    "records_used": {k: cell(v, "RECORD") for k, v in REC.items()} | {"contribution_margin_by_line": {k: cell(v, "RECORD") for k, v in CM.items()}},
    "assumptions": ASSUME,
    "assumption_values": {k: (v if isinstance(v, list) else round(v, 4)) for k, v in A.items()},
    "missing_from_pack": MISSING,
    "sensitivities": SENS,
    "check": dict(method="Five figures recomputed by closed-form annual arithmetic, independent of the period functions", results=CHECK),
    "flags_for_tripp": FLAGS,
}
OUT_JSON.write_text(json.dumps(doc, indent=1))

# ---------------------------------------------------------------- Markdown
def f1(x): return f"{x:,.1f}"
def tbl(header, body):
    s = "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n"
    return s + "".join("| " + " | ".join(r) + " |\n" for r in body)

cols = ["FY2025", "FY2026"] + QP + ["FY2027", "FY2028"]
short = lambda p: p.replace("FY20", "").replace(" ", "")
def brow(grp, key, name, fmt=f1):
    return [name] + [fmt(B[p][grp][key]) for p in cols]
md = [f"# Larkspur central projection, FY2027–FY2028 (no climate event)\n",
      f"Week 4 step 1 · run `{RUN_ID}` · built by `scenarios/build_central_projection.py` · full labelled data in `central-projection.json`. "
      "Draft for Tripp's review. FY2025 = RECORD (pack); FY2026 = bridge estimate; every projected figure is MODEL built on the ASSUMPTIONS listed below. $M unless stated.\n",
      "## What the projection assumes\n", " ".join(SENTENCES) + "\n",
      "## FY2025 reconciles to the pack\n",
      tbl(["Item", "Pack", "Model", "OK", "Source"], [[r["item"], f"{r['pack']:,}", f"{r['model']:,}", "yes" if r["ok"] else "NO", r["src"]] for r in RECON]),
      "\nBeverage EBITDA reconciles by construction: fixed cost ($81.2M) is the figure that makes recorded line margins meet the recorded $67.6M. Revenue, Gonzales contribution and the Larkspur totals reconcile independently.\n",
      "## Beverage by quarter\n",
      tbl(["Gonzales lines (BV-03 to 06)"] + [short(p) for p in cols], [
          brow("gonzales", "cases_k", "Cases, k", lambda x: f"{x:,.0f}"), brow("gonzales", "utilisation_pct", "Utilisation %", lambda x: f"{x:.0f}"),
          brow("gonzales", "revenue", "Revenue"), brow("gonzales", "variable_cost", "Variable cost"), brow("gonzales", "fixed_cost", "Fixed cost"),
          brow("gonzales", "of_which_launch", "of which launch"), brow("gonzales", "ebitda", "EBITDA"),
          brow("gonzales", "fg_inventory_cases_k", "FG on hand, k cases", lambda x: f"{x:,.0f}"), brow("gonzales", "fg_inventory_usd", "FG on hand, $M")]),
      "\n",
      tbl(["Other lines + Beverage total"] + [short(p) for p in cols], [
          brow("other_lines", "revenue", "Other lines revenue"), brow("other_lines", "ebitda", "Other lines EBITDA"),
          brow("total", "revenue", "Beverage revenue"), brow("total", "variable_cost", "Beverage variable cost"), brow("total", "fixed_cost", "Beverage fixed cost"),
          brow("total", "ebitda", "Beverage EBITDA"), brow("total", "fg_inventory_usd", "Beverage FG on hand, $M")]),
      "\n## Larkspur-wide net debt and leverage\n",
      tbl(["Larkspur"] + [short(p) for p in cols], [
          ["Adjusted EBITDA (period)"] + [f1(C[p]["ebitda"]) for p in cols],
          ["EBITDA, LTM"] + [f1(LEV[p]["ltm_ebitda"]) for p in cols],
          ["Net debt, period end"] + [f1(LEV[p]["net_debt"]) for p in cols],
          ["Leverage (3.50x covenant)"] + [pf(p) for p in cols],
          ["Headroom before 3.50x"] + [f1(LEV[p]["headroom"]) for p in cols]]),
      "\nAt the mid-October test (Q3-end net debt + $93M harvest build):\n\n",
      tbl(["Test", "Net debt at test", "LTM EBITDA", "Leverage", "Headroom"],
          [[k, f1(v["net_debt_at_test"]), f1(v["ltm_ebitda"]), f"{v['leverage']:.2f}x", f1(v["headroom"])] for k, v in OCT.items()]),
      "\n## Assumptions (ours, to confirm)\n",
      "".join(f"- **{a['id']}**: {a['value']}. {a['why']}. Confirm: {a['who']}.\n" for a in ASSUME),
      "\n## Sensitivities (MODEL)\n", "".join(f"- {s['change']}: {s['effect']}\n" for s in SENS),
      "\n## Check\n", "Recomputed a second way with closed-form annual arithmetic: " +
      "; ".join(f"{c['item']} {c['main']} vs {c['check']}" for c in CHECK) + ". All agree.\n",
      "\n## Missing from the pack\n", "".join(f"- {m}\n" for m in MISSING),
      "\n## Flags for Tripp\n", "".join(f"{i}. {f}\n" for i, f in enumerate(FLAGS, 1))]
OUT_MD.write_text("\n".join(md))
print(f"{RUN_ID}: wrote {OUT_JSON.name} and {OUT_MD.name}")
for k in ("beverage_ebitda", "gonzales_ebitda", "larkspur_ebitda", "net_debt_year_end", "leverage_year_end", "october_test"):
    print(k, summary[k])
