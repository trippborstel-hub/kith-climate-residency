"""Week 4 step 3: response A2, a second qualified aseptic site, tested against all three stories.

Stories: the central projection (P-20261009-01); the flood with the expected reaction (shelf comes back); the flood with the
unexpected reaction (Lakemont delists the Gonzales lines from 1 March 2028). Both flood paths are from P-20261009-02.

A2 as modelled: Larkspur decides by mid-November 2026, qualifies a second aseptic co-packer (process-authority validation,
regulatory filings, line trials: copacker Art. 14.1), and from the day it is saleable moves to it the volume above Gonzales's
15.0M-case minimum (Art. 3.2), capped at 4.0M cases a year. Gonzales is filled first up to the minimum, so moving volume never
creates a shortfall charge. Moving 4.0M cases leaves Gonzales with about 21% spare capacity, which is what rebuilds the buffer.

Method: a daily stock balance in days of Gonzales-line demand, written for two sources (it reduces to Week 3's simulate() when
nothing is moved; checked below). Money uses the central projection's quarterly rates, priced the same way as P-20261009-02.

Sources: scenarios/central-projection.json, scenarios/flood-delisting.json, scenarios/run_scenarios.py (simulate, read only);
client records: copacker-agreement-excerpt.md (minimum, capacity, Art. 14 qualification, 6-9 months), credit-agreement-excerpt.md
($85.0M capex covenant), retailer-sla-excerpt.md, insurance-program-summary.md, logistics-note.md.

Run:  ~/.venvs/kith-climate/bin/python scenarios/build_a2_second_site.py     (from 3 Larkspur/)
Writes scenarios/a2-second-site.json and scenarios/a2-second-site.md only.
"""
import calendar, datetime as dt, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_scenarios as W3   # read only

CP = json.loads((HERE / "central-projection.json").read_text())
FD = json.loads((HERE / "flood-delisting.json").read_text())
RUN_ID = "P-20261009-03"
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

QS = [f"FY{y} Q{q}" for y in (2027, 2028) for q in (1, 2, 3, 4)]
def row(b, k): return next(r for r in CP["beverage"][b] if r["key"] == k)["values"]
def lrow(g, k): return next(r for r in CP["larkspur"][g] if r["key"] == k)["values"]
g_rev = {q: row("gonzales", "revenue")[q]["v"] for q in QS}
g_var = {q: row("gonzales", "variable_cost")[q]["v"] for q in QS}
g_cases = {q: row("gonzales", "cases_k")[q]["v"] for q in QS}
b_rev = {q: row("total", "revenue")[q]["v"] for q in QS}
cm = {q: 1 - g_var[q] / g_rev[q] for q in QS}
def qof(d): return f"FY{d.year} Q{(d.month - 1) // 3 + 1}"
def qbounds(q):
    y, n = int(q[2:6]), int(q[-1])
    return dt.date(y, 3 * n - 2, 1), dt.date(y, 3 * n, calendar.monthrange(y, 3 * n)[1])
def qdays(q): a, b = qbounds(q); return (b - a).days + 1

# ---------------------------------------------------------------- records and assumptions
REC = dict(min_commit_k=15000.0, rated_k=19000.0, buffer=27, staged=14, cbi_limit=10.0, cbi_wait=30, covenant=3.5, capex_cap=85.0,
           cust_bev={"Lakemont": 160.0, "Fairmount": 105.0, "Callahan": 20.0}, bev_fy2025=520.0)
A = dict(
    decide="2026-11-15",
    timings={"6 months (qualified 15 May 2027)": "2027-05-15",       # Art. 14.2: last line took 6-9 months, same facility
             "9 months (qualified 15 Aug 2027)": "2027-08-15",
             "decision slips to mid-February (qualified 15 Nov 2027)": "2027-11-15"},
    base_timing="9 months (qualified 15 Aug 2027)",
    move_cap_k=4000.0,             # volume above the 15.0M minimum, at most 4.0M cases a year
    one_time_opex=2.5,             # validation, filings, trials ($M), FY2027 H1
    one_time_capex=3.5,            # duplicate filler change parts and tooling ($M), FY2027 H1
    premium=0.04,                  # extra variable cost on moved volume: smaller runs, freight to Romeoville
    surge=0.0,                     # extra second-site output after a Gonzales stop, as a share of its normal volume
    flood="2027-08-12", days_down=105, delist_from="2028-03-01", lakemont_share=160 * 0.6 / 312,
    tax=0.25, rate=0.07, peak_build=93.0, cbi_paid_q="FY2028 Q1",
)
d0 = dt.date.fromisoformat(A["flood"])
SEASON_2028 = dt.date(2028, 6, 1)

# ---------------------------------------------------------------- daily model with two sources
def moved_share(q, delisted=False):
    """Share of Gonzales-line demand filled at the second site once qualified (Gonzales filled first up to its minimum)."""
    demand = g_cases[q] * (1 - (A["lakemont_share"] if delisted else 0))
    return max(0.0, min(A["move_cap_k"] / 4, demand - REC["min_commit_k"] / 4)) / demand

def simulate2(qual, delisting, horizon=720):
    qual = dt.date.fromisoformat(qual) if qual else None
    f0 = dt.date.fromisoformat(A["delist_from"])
    s0 = moved_share(qof(d0)) if qual and qual <= d0 else 0.0
    inv = REC["buffer"] - REC["staged"] * (1 - s0)            # stock staged at Gonzales is lost; second-site stock is not
    unmet, stock = [], []
    for t in range(horizon):
        d = d0 + dt.timedelta(days=t)
        q = qof(d) if qof(d) in g_cases else "FY2028 Q4"
        delisted = delisting and d >= f0
        dem = 1.0 - (A["lakemont_share"] if delisted else 0.0)  # in units of a full day of central Gonzales-line demand
        s = moved_share(q, delisted) if qual and d >= qual else 0.0
        desired = max(0.0, dem + REC["buffer"] * dem - inv)    # meet demand and close the gap to target (less when above it)
        second = min(desired, s * dem * (1 + (A["surge"] if t < A["days_down"] else 0.0)))
        gonz_cap = 0.0 if t < A["days_down"] else REC["rated_k"] / 4 / g_cases[q]   # Gonzales rated capacity in days of demand
        prod = second + min(gonz_cap, desired - second)
        avail = inv + prod
        ship = min(dem, avail)
        inv = avail - ship
        unmet.append(dem - ship)
        stock.append(inv / dem)
    return unmet, stock

# check: with nothing moved, the two-source model gives Week 3's answer
u_chk, _ = simulate2(None, False)
w3 = W3.simulate([(0, A["days_down"])], staged_lost=True, cap_ratio=1.0)
CHECK = [dict(item="Days lost with no second site: this model vs Week 3 simulate()", main=round(sum(u_chk), 2), check=round(w3["lost_days"], 2))]

# ---------------------------------------------------------------- money
def a2_costs(qual):
    """A2's own cost against the central projection, by quarter: one-time cost in FY2027 H1, premium on moved volume after qualification."""
    qd = dt.date.fromisoformat(qual)
    out = {}
    for q in QS:
        a, b = qbounds(q)
        frac = max(0, (b - max(a, qd)).days + 1) / qdays(q) if b >= qd else 0.0
        moved_var = moved_share(q) * frac * g_var[q]
        one = A["one_time_opex"] / 2 if q in ("FY2027 Q1", "FY2027 Q2") else 0.0
        cap = A["one_time_capex"] / 2 if q in ("FY2027 Q1", "FY2027 Q2") else 0.0
        out[q] = dict(premium=-A["premium"] * moved_var, one_time=-one, capex=-cap)
    return out

def flood_money(unmet, qual):
    days = [d0 + dt.timedelta(days=t) for t in range(len(unmet))]
    q = {k: dict(lost_contribution=0.0, credits=0.0, stock=0.0, insurance=0.0, lost_revenue=0.0) for k in QS}
    for d, u in zip(days, unmet):
        k = qof(d)
        if k in q:
            q[k]["lost_revenue"] += u * g_rev[k] / qdays(k)
            q[k]["lost_contribution"] += u * g_rev[k] / qdays(k) * cm[k]
    s0 = moved_share(qof(d0)) if qual and dt.date.fromisoformat(qual) <= d0 else 0.0
    q[qof(d0)]["stock"] = REC["staged"] * (1 - s0) * g_var[qof(d0)] / qdays(qof(d0))
    months, fills = {}, []
    for d, u in zip(days, unmet): months.setdefault((d.year, d.month), []).append(u)
    for (y, m), us in sorted(months.items()):
        k = f"FY{y} Q{(m - 1) // 3 + 1}"
        if k not in q or sum(us) < 1e-9: continue
        nd = calendar.monthrange(y, m)[1]
        share, g = sum(us) / nd, g_rev[k] / b_rev[k]
        fill = 100 * (1 - g * share)
        rate = 0.05 if fill < 97 else 0.03 if fill < 98.5 else 0.0
        c = rate * sum(REC["cust_bev"].values()) * (b_rev[k] * 4) / REC["bev_fy2025"] * nd / 365 * (1 - g * share)
        q[k]["credits"] += c
        fills.append(dict(month=f"{y}-{m:02d}", fill=round(fill, 1)))
    run = longest = 0
    for f in fills:
        run = run + 1 if f["fill"] < 96 else 0
        longest = max(longest, run)
    after = sum(u * g_rev[qof(d)] / qdays(qof(d)) * cm[qof(d)] for d, u in zip(days[REC["cbi_wait"]:], unmet[REC["cbi_wait"]:]) if qof(d) in cm)
    q[A["cbi_paid_q"]]["insurance"] = min(REC["cbi_limit"], after)
    return q, fills, longest

def delist_money():
    f0 = dt.date.fromisoformat(A["delist_from"])
    out = {}
    for k in QS:
        a, b = qbounds(k)
        cov = max(0, (b - max(a, f0)).days + 1) if b >= f0 else 0
        lr = A["lakemont_share"] * g_rev[k] * cov / qdays(k)
        out[k] = lr * cm[k]
    return out

def evaluate(story, qual):
    costs = a2_costs(qual) if qual else {k: dict(premium=0.0, one_time=0.0, capex=0.0) for k in QS}
    if story == "central":
        fl = {k: dict(lost_contribution=0.0, credits=0.0, stock=0.0, insurance=0.0) for k in QS}; fills, longest, stock = [], 0, None
    else:
        unmet, stock = simulate2(qual, story == "unexpected")
        fl, fills, longest = flood_money(unmet, qual)
    dl = delist_money() if story == "unexpected" else {k: 0.0 for k in QS}
    if story == "unexpected" and qual:   # after delisting Gonzales demand is under its minimum, so nothing is moved: no premium
        f0 = dt.date.fromisoformat(A["delist_from"])
        for k in QS:
            if qbounds(k)[0] >= dt.date(2028, 4, 1): costs[k]["premium"] = 0.0
            elif qbounds(k)[1] >= f0: costs[k]["premium"] *= (f0 - qbounds(k)[0]).days / qdays(k)
    Q, cum = {}, 0.0
    for k in QS:
        e = -fl[k]["lost_contribution"] - fl[k]["credits"] - fl[k]["stock"] + fl[k]["insurance"] - dl[k] + costs[k]["premium"] + costs[k]["one_time"]
        cash = e + fl[k]["stock"] + costs[k]["capex"]
        interest = A["rate"] / 4 * cum
        d_nd = -cash + interest + A["tax"] * (e - interest)
        cum += d_nd
        Q[k] = dict(ebitda=e, a2_cost=costs[k]["premium"] + costs[k]["one_time"], a2_capex=costs[k]["capex"], cum_net_debt=cum)
    octs = {}
    for yr in (2027, 2028):
        k = f"FY{yr} Q3"; i = QS.index(k)
        ltm = lrow("debt", "ltm_ebitda")[k]["v"] + sum(Q[x]["ebitda"] for x in QS[max(0, i - 3):i + 1])
        nd = lrow("debt", "net_debt")[k]["v"] + Q[k]["cum_net_debt"] + A["peak_build"]
        octs[f"Oct {yr}"] = dict(leverage=nd / ltm, headroom=ltm - nd / REC["covenant"])
    buf = None if stock is None else stock[(SEASON_2028 - d0).days]
    lost = None if story == "central" else sum(unmet)
    return dict(fy2027=sum(Q[k]["ebitda"] for k in QS[:4]), fy2028=sum(Q[k]["ebitda"] for k in QS[4:]), quarters=Q, october=octs,
                buffer_days_1_jun_2028=buf if buf is not None else REC["buffer"], days_lost=lost, months_under_96=longest,
                review_triggered=longest >= 3, fills=fills, net_debt_end_fy2028=Q["FY2028 Q4"]["cum_net_debt"])

STORIES = ["central", "expected", "unexpected"]
RES = {}
for story in STORIES:
    RES[story] = {"without A2": evaluate(story, None)}
    for name, qd in A["timings"].items():
        RES[story][name] = evaluate(story, qd)

# second check: without A2, the flood paths match the published P-20261009-02 figures
for story, path in (("expected", "expected"), ("unexpected", "unexpected")):
    for y in ("FY2027", "FY2028"):
        CHECK.append(dict(item=f"{story} {y} EBITDA without A2: this model vs P-20261009-02",
                          main=round(RES[story]["without A2"][y.lower()], 2), check=round(FD["paths"][path]["years"][y]["ebitda"], 2)))
for c in CHECK: c["agree"] = abs(c["main"] - c["check"]) < 0.1
assert all(c["agree"] for c in CHECK), CHECK

# coverage needed to keep category fill at 96% while Gonzales is down (closed form)
g_q3 = g_rev["FY2027 Q3"] / b_rev["FY2027 Q3"]
coverage_needed = 1 - 0.04 / g_q3
base = A["base_timing"]
SENS = []
for label, over in (("Surge: second site lifts output 50% while Gonzales is down", dict(surge=0.5)),
                    ("Premium 8% on moved volume, not 4%", dict(premium=0.08)),
                    ("One-time cost doubles ($5.0M opex, $7.0M capex)", dict(one_time_opex=5.0, one_time_capex=7.0))):
    keep = {k: A[k] for k in over}; A.update(over)
    r = evaluate("expected", A["timings"][base]); A.update(keep)
    SENS.append(dict(change=label, expected_fy2027=round(r["fy2027"], 1), expected_fy2028=round(r["fy2028"], 1),
                     review_triggered=r["review_triggered"], buffer_1_jun_2028=round(r["buffer_days_1_jun_2028"], 1)))

# ---------------------------------------------------------------- statements
def gain(story, timing, y): return RES[story][timing][y] - RES[story]["without A2"][y]
two = lambda story, t: gain(story, t, "fy2027") + gain(story, t, "fy2028")
fast = list(A["timings"])[0]; slip = list(A["timings"])[2]
E, U, C0 = RES["expected"], RES["unexpected"], RES["central"]
def says(x):
    return f"improves FY2027-28 EBITDA by ${x:.1f}M" if x > 0.5 else f"costs a net ${-x:.1f}M of FY2027-28 EBITDA" if x < -0.5 else f"roughly breaks even on FY2027-28 EBITDA ({x:+.1f}M)"

# what the 2028 buffer is worth if an Ida-sized stop (25 days, Week 3 S1 high) hits on 29 August 2028: conditional, no probability
ida_q = "FY2028 Q3"
ida_lost_without = 25.0 - E["without A2"]["buffer_days_1_jun_2028"]     # no cover and no spare: every stopped day is a lost day
ida_lost_with = max(0.0, 25.0 * (1 - moved_share(ida_q)) - E[base]["buffer_days_1_jun_2028"])
ida_cost = lambda days: days * g_rev[ida_q] / qdays(ida_q) * cm[ida_q]
IDA2028 = dict(days_lost_without_a2=ida_lost_without, days_lost_with_a2=ida_lost_with,
               contribution_without_a2=ida_cost(ida_lost_without), contribution_with_a2=ida_cost(ida_lost_with), label="MODEL, conditional on the stop happening")
STATEMENTS = {
    "central": f"With no climate event, choosing A2 costs ${-two('central', base):.1f}M of EBITDA over FY2027-28 (${-sum(C0[base]['quarters'][k]['a2_capex'] for k in QS):.1f}M capex on top), "
               f"because Larkspur pays to qualify a site and a {A['premium']*100:.0f}% premium on the {A['move_cap_k']/1000:.1f}M cases it moves; in return Gonzales gets about 21% spare capacity, which the central case does not have.",
    "expected": f"Under the flood with the shelf coming back, choosing A2 (qualified by mid-August) {says(two('expected', base))} but starts the 2028 hurricane season with "
                f"{E[base]['buffer_days_1_jun_2028']:.0f} days of stock instead of {E['without A2']['buffer_days_1_jun_2028']:.0f}, because the second site keeps filling about a fifth of the lines while Gonzales is down "
                f"and the freed capacity rebuilds the buffer after restart. If an Ida-sized stop then hit in late August 2028, that buffer is the difference between "
                f"${IDA2028['contribution_without_a2']:.1f}M of contribution lost with empty shelves from day one, and ${IDA2028['contribution_with_a2']:.1f}M. "
                f"A2 does not stop the category review: fill stays under 96% for {E[base]['months_under_96']} months.",
    "unexpected": f"Under the flood with Lakemont delisting, choosing A2 {says(two('unexpected', base))}, because the shorter shortage in FY2027 roughly pays for the site; "
                  f"it does nothing for the delisting itself, which A2 does not prevent, or for the shortfall against the Gonzales minimum, which is the same with or without it.",
    "timing": f"Timing decides the money: qualified by May, A2 {says(two('expected', fast))} in the expected path; if the decision slips to February and the site is ready in mid-November, it {says(two('expected', slip))}.",
    "coverage": f"To keep category fill at 96% with Gonzales down, the second site would need about {coverage_needed*100:.0f}% of the Gonzales lines' volume, close to full dual sourcing. "
                f"Sized to the minimum-commitment headroom, A2 cannot prevent a category review; it limits the damage and rebuilds the buffer.",
}

ASSUME = [
    ("Decision 15 November 2026; saleable after 6 or 9 months (base 9), or 15 November 2027 if the decision slips three months", "Art. 14.2 records 6-9 months for the last line at the same facility; a new site could take longer"),
    ("Volume moved: what is above Gonzales's 15.0M-case minimum, at most 4.0M cases a year (about 21%)", "Keeps Gonzales at its minimum so no shortfall charge; the candidate site's capacity is not in the pack"),
    ("One-time cost $2.5M expensed and $3.5M capex, in FY2027 H1", "Not in the pack (Week 3 gap: 'cost and candidate sites'); capex stays under the $85.0M covenant cap"),
    ("Running premium 4% of variable cost on moved volume", "Smaller runs and freight to Romeoville; not in the pack"),
    ("No surge at the second site after a Gonzales stop (sensitivity at +50%)", "Its spare capacity is unknown"),
    ("Second-site stock is not lost in the flood; staged stock at Gonzales is lost in proportion to its share", "Different site, different flood exposure; the candidate site is unknown"),
    ("After a delisting all remaining volume returns to Gonzales, so the premium stops; no second-site minimum", "Contract terms for a second site are not known"),
]
doc = dict(
    _about="Week 4 step 3: response A2 tested against the central projection and both flood paths. All results MODEL; inputs labelled. Built by scenarios/build_a2_second_site.py.",
    run=dict(run_id=RUN_ID, run_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), baselines=["P-20261009-01", "P-20261009-02"],
             script="scenarios/build_a2_second_site.py", script_sha256=sha(__file__),
             inputs={f: sha(HERE / f) for f in ("central-projection.json", "flood-delisting.json", "run_scenarios.py")}),
    statements=STATEMENTS, results=RES, ida_2028_if_it_happens=IDA2028, sensitivities=SENS, coverage_needed_for_96pct_fill=coverage_needed,
    assumptions=[dict(value=a, why=w, label="ASSUMPTION") for a, w in ASSUME],
    records=dict(min_commit_k=REC["min_commit_k"], rated_k=REC["rated_k"], qualification_months="6-9", capex_covenant=REC["capex_cap"], label="RECORD"),
    check=CHECK,
)
def clean(o):
    if isinstance(o, float): return round(o, 2)
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    return o
(HERE / "a2-second-site.json").write_text(json.dumps(clean(doc), indent=1))

# ---------------------------------------------------------------- markdown
f1 = lambda x: f"{(0.0 if abs(x) < 0.05 else x):+,.1f}"
def tbl(h, rows): return "| " + " | ".join(h) + " |\n|" + "---|" * len(h) + "\n" + "".join("| " + " | ".join(r) + " |\n" for r in rows)
names = {"central": "Central (no event)", "expected": "Flood, shelf comes back", "unexpected": "Flood, Lakemont delists"}
rows = []
for s in STORIES:
    for t in ["without A2"] + list(A["timings"]):
        r = RES[s][t]
        rows.append([names[s] if t == "without A2" else "", "No A2" if t == "without A2" else "A2, " + t.split(" (")[0],
                     f1(r["fy2027"]), f1(r["fy2028"]), f"{r['october']['Oct 2027']['leverage']:.2f}x", f"{r['october']['Oct 2028']['leverage']:.2f}x",
                     f"{r['buffer_days_1_jun_2028']:.0f}", "yes" if r["review_triggered"] else "no"])
md = f"""# Response A2: a second aseptic site

Week 4 step 3 · run `{RUN_ID}` against `P-20261009-01` (central) and `P-20261009-02` (flood to delisting) · built by `scenarios/build_a2_second_site.py` · data in `a2-second-site.json`. Draft for Tripp's review. Results are MODEL; the cost and site inputs are ASSUMPTIONS because the pack has neither.

**A2 as tested:** decide by 15 November 2026 and qualify a second aseptic co-packer, the 6 to 9 months Art. 14.2 records. From the day it is saleable, it fills whatever volume sits above Gonzales's 15.0M-case minimum, up to 4.0M cases a year (about 21%). Gonzales is never pushed under its minimum, and it gains the spare capacity it lacks in the central case.

## The answer, story by story

- **Central:** {STATEMENTS['central']}
- **Expected:** {STATEMENTS['expected']}
- **Unexpected:** {STATEMENTS['unexpected']}
- **Timing:** {STATEMENTS['timing']}
- **What A2 cannot do:** {STATEMENTS['coverage']}

## Results (EBITDA change against the central projection, $M)

{tbl(["Story", "Response", "FY2027", "FY2028", "Oct 2027 test", "Oct 2028 test", "Stock days on 1 Jun 2028", "Category review"], rows)}
## Sensitivities (flood with the shelf back, A2 at 9 months)

{tbl(["Change", "FY2027", "FY2028", "Review", "Stock days 1 Jun 2028"], [[s['change'], f1(s['expected_fy2027']), f1(s['expected_fy2028']), "yes" if s['review_triggered'] else "no", f"{s['buffer_1_jun_2028']:.0f}"] for s in SENS])}
## Assumptions (ours)

{"".join(f"- {a}. {w}." + chr(10) for a, w in ASSUME)}
## Check

{"; ".join(f"{c['item']}: {c['main']} vs {c['check']}" for c in CHECK)}. All agree.
"""
(HERE / "a2-second-site.md").write_text(md)
print(RUN_ID)
for k, v in STATEMENTS.items(): print("-", k, ":", v)
print(tbl(["Story", "Response", "FY2027", "FY2028", "Oct27", "Oct28", "Stock 1 Jun 28", "Review"], rows))
for s in SENS: print(s)
