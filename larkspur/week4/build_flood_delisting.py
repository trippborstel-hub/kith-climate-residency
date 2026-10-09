"""Week 4 step 2: the flood-to-delisting story, measured against the central projection (P-20261009-01).

Story (Tripp's choice, 9 Oct 2026): water enters the Gonzales co-packer (Week 3 case S2) -> retail fill stays under 96% for three
months -> category review (retailer SLA 6.3). EXPECTED reaction: the review closes and the shelf comes back. UNEXPECTED: Lakemont
delists the Gonzales lines at its February joint business plan review. A variant has all three retailers delist.

Method: Week 3's daily stock model (run_scenarios.simulate, imported, not edited) gives unmet demand by day. Money uses the central
projection's quarterly Gonzales revenue and margin, so the loss is priced at FY2027-28 rates, not FY2025. Effects are deltas
against the central projection, quarter by quarter, then applied to its EBITDA, net debt and the October covenant tests.

Sources: scenarios/central-projection.json; scenarios/run_scenarios.py (simulate); client records in
client data/windward-risk-advisors/clients/larkspur-foods/: retailer-sla-excerpt.md (fill terms, February JBP review),
insurance-program-summary.md ($10.0M contingent BI after 30 days), copacker-agreement-excerpt.md (15.0M case minimum, Art. 11),
reference.md (customer Beverage revenue), logistics-note.md (27 and 14 days).

Run:  ~/.venvs/kith-climate/bin/python scenarios/build_flood_delisting.py     (from 3 Larkspur/)
Writes scenarios/flood-delisting.json and scenarios/flood-delisting.md only.
"""
import calendar, datetime as dt, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_scenarios as W3   # Week 3 model, read only

PACK = W3.PACK
CP = json.loads((HERE / "central-projection.json").read_text())
RUN_ID = "P-20261009-02"
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def row(block, key):
    return next(r for r in CP["beverage"][block] if r["key"] == key)["values"]
def lrow(group, key):
    return next(r for r in CP["larkspur"][group] if r["key"] == key)["values"]

QS = [f"FY{y} Q{q}" for y in (2027, 2028) for q in (1, 2, 3, 4)]
def qof(d): return f"FY{d.year} Q{(d.month - 1) // 3 + 1}"
def qdays(q):
    y, n = int(q[2:6]), int(q[-1])
    return sum(calendar.monthrange(y, m)[1] for m in range(3 * n - 2, 3 * n + 1))

g_rev = {q: row("gonzales", "revenue")[q]["v"] for q in QS}
g_var = {q: row("gonzales", "variable_cost")[q]["v"] for q in QS}
g_cases = {q: row("gonzales", "cases_k")[q]["v"] for q in QS}
b_rev = {q: row("total", "revenue")[q]["v"] for q in QS}
cm = {q: 1 - g_var[q] / g_rev[q] for q in QS}

# ---------------------------------------------------------------- records and assumptions
REC = dict(staged_days=14, buffer_days=27, fill_review=96.0, fill_credit=98.5, fill_credit_high=97.0, credit=0.03, credit_high=0.05,
           cbi_limit=10.0, cbi_wait=30, min_commit_k=15000.0, rated_k=19000.0,
           cust_bev={"Lakemont": 160.0, "Fairmount": 105.0, "Callahan": 20.0}, bev_fy2025=520.0, covenant=3.5)
A = dict(
    start="2027-08-12",            # Week 3 S2 date: the August 2016 flood's calendar day, placed in 2027
    days_down=105,                 # Week 3 S2 midpoint of 60 to 150
    cap_ratio=1.0,                 # central projection: Gonzales full from Q2 FY2027, so no spare capacity to rebuild the buffer
    gonz_share_of_retailer=0.60,   # Week 3: each retailer's Beverage buying is 60% Gonzales lines
    delist_from="2028-03-01",      # decided at the February 2028 joint business plan review (SLA Schedule 6-A), effective 1 March
    delist_months=12,              # Week 3 what-if basis; runs past the FY2028 window
    cbi_paid_q="FY2028 Q1",        # claim settled and paid about five months after the loss
    tax=0.25, rate=0.07, peak_build=93.0,   # as in the central projection
)
d0 = dt.date.fromisoformat(A["start"])

# ---------------------------------------------------------------- operating: the daily model
sim = W3.simulate([(0, A["days_down"])], staged_lost=True, cap_ratio=A["cap_ratio"])
unmet, stock = sim["unmet"], sim["stock"]
days = [d0 + dt.timedelta(days=t) for t in range(len(unmet))]

lost_days_q = {q: 0.0 for q in QS}
for d, u in zip(days, unmet):
    if qof(d) in lost_days_q: lost_days_q[qof(d)] += u

def rev_per_day(q): return g_rev[q] / qdays(q)

# ---------------------------------------------------------------- money: the flood (common to both paths)
flood = {q: dict(lost_revenue=0.0, lost_contribution=0.0, credits=0.0, stock_written_off=0.0, insurance=0.0) for q in QS}
for q in QS:
    lr = lost_days_q[q] * rev_per_day(q)
    flood[q]["lost_revenue"] = lr
    flood[q]["lost_contribution"] = lr * cm[q]
q0 = qof(d0)
flood[q0]["stock_written_off"] = REC["staged_days"] * g_var[q0] / qdays(q0)

months, fills = {}, []
for d, u in zip(days, unmet):
    months.setdefault((d.year, d.month), []).append(u)
for (y, m), us in sorted(months.items()):
    q = f"FY{y} Q{(m - 1) // 3 + 1}"
    if q not in flood or sum(us) == 0: continue
    nd = calendar.monthrange(y, m)[1]
    share = sum(us) / nd
    g = g_rev[q] / b_rev[q]
    fill = 100 * (1 - g * share)
    rate = REC["credit_high"] if fill < REC["fill_credit_high"] else REC["credit"] if fill < REC["fill_credit"] else 0.0
    sla_rev_year = sum(REC["cust_bev"].values()) * (b_rev[q] * 4) / REC["bev_fy2025"]
    c = rate * sla_rev_year * nd / 365 * (1 - g * share)        # all Beverage invoices to the three retailers (Week 3 high basis)
    flood[q]["credits"] += c
    fills.append(dict(month=f"{y}-{m:02d}", category_fill_pct=round(fill, 1), credit_rate=rate, credit=round(c, 2)))
run, months_under = 0, 0
for f in fills:
    run = run + 1 if f["category_fill_pct"] < REC["fill_review"] else 0
    months_under = max(months_under, run)
review_month = next(f["month"] for i, f in enumerate(fills) if i >= 2 and all(x["category_fill_pct"] < 96 for x in fills[i - 2:i + 1]))

after_wait = sum(u * rev_per_day(qof(d)) * cm[qof(d)] for d, u in zip(days[REC["cbi_wait"]:], unmet[REC["cbi_wait"]:]) if qof(d) in cm)
cbi = min(REC["cbi_limit"], after_wait)
flood[A["cbi_paid_q"]]["insurance"] = cbi

# ---------------------------------------------------------------- money: the delisting
def delisting(retailers):
    share = sum(REC["cust_bev"][r] for r in retailers) * A["gonz_share_of_retailer"] / 312.0   # share of Gonzales revenue
    f0 = dt.date.fromisoformat(A["delist_from"])
    out = {}
    for q in QS:
        y, n = int(q[2:6]), int(q[-1])
        qs_, qe = dt.date(y, 3 * n - 2, 1), dt.date(y, 3 * n, calendar.monthrange(y, 3 * n)[1])
        covered = max(0, (qe - max(qs_, f0)).days + 1) if qe >= f0 else 0
        lr = share * g_rev[q] * covered / qdays(q)
        out[q] = dict(lost_revenue=lr, lost_contribution=lr * cm[q], lost_cases_k=share * g_cases[q] * covered / qdays(q))
    return share, out

PATHS = {"expected": [], "unexpected": ["Lakemont"], "variant_all_three": ["Lakemont", "Fairmount", "Callahan"]}

def build(path):
    share, dl = delisting(PATHS[path]) if PATHS[path] else (0.0, {q: dict(lost_revenue=0.0, lost_contribution=0.0, lost_cases_k=0.0) for q in QS})
    qrows, cum_nd = {}, 0.0
    for q in QS:
        f, d = flood[q], dl[q]
        rev = -(f["lost_revenue"] + d["lost_revenue"])
        contrib = -(f["lost_contribution"] + d["lost_contribution"])
        ebitda = contrib - f["credits"] - f["stock_written_off"] + f["insurance"]
        cash_pre_tax = ebitda + f["stock_written_off"]               # write-off is non-cash: the stock was paid for before the flood
        interest = A["rate"] / 4 * cum_nd                             # on the extra debt carried so far
        d_nd = -cash_pre_tax + interest + A["tax"] * (ebitda - interest)   # cash lost, less the tax it saves
        cum_nd += d_nd
        cases = g_cases[q] - lost_days_q[q] * g_cases[q] / qdays(q) - d["lost_cases_k"]
        qrows[q] = dict(revenue=rev, variable_cost_saved=rev - contrib, lost_contribution=contrib, service_credits=-f["credits"],
                        stock_written_off=-f["stock_written_off"], insurance=f["insurance"], ebitda=ebitda,
                        net_debt_change=d_nd, cumulative_net_debt_change=cum_nd, gonzales_cases_k=cases)
    # finished goods (days of cover at quarter end)
    f0 = dt.date.fromisoformat(A["delist_from"])
    spare = 1 / (1 - share) if share else A["cap_ratio"]
    def cover_at(date):
        t = (date - d0).days
        if t < 0: return REC["buffer_days"]
        if share and date >= f0:
            t0 = (f0 - d0).days
            return min(REC["buffer_days"], stock[t0] + (spare - 1) * (t - t0))
        return stock[min(t, len(stock) - 1)]
    for q in QS:
        y, n = int(q[2:6]), int(q[-1])
        qrows[q]["fg_cover_days_end"] = cover_at(dt.date(y, 3 * n, calendar.monthrange(y, 3 * n)[1]))
    # whole-company effect and the covenant
    led = {}
    for q in QS:
        e0 = lrow("ebitda", "ebitda")[q]["v"]
        ltm_idx = QS.index(q)
        ltm_delta = sum(qrows[x]["ebitda"] for x in QS[max(0, ltm_idx - 3):ltm_idx + 1])
        ltm = lrow("debt", "ltm_ebitda")[q]["v"] + ltm_delta
        nd = lrow("debt", "net_debt")[q]["v"] + qrows[q]["cumulative_net_debt_change"]
        led[q] = dict(ebitda=e0 + qrows[q]["ebitda"], ltm_ebitda=ltm, net_debt=nd, leverage=nd / ltm, headroom=ltm - nd / REC["covenant"])
    octs = {}
    for yr in (2027, 2028):
        q = f"FY{yr} Q3"
        nd = led[q]["net_debt"] + A["peak_build"]
        octs[f"Oct {yr}"] = dict(net_debt_at_test=nd, ltm_ebitda=led[q]["ltm_ebitda"], leverage=nd / led[q]["ltm_ebitda"],
                                 headroom=led[q]["ltm_ebitda"] - nd / REC["covenant"],
                                 central_leverage=CP["larkspur"]["october_test"][f"Oct {yr}"]["leverage"]["v"],
                                 central_headroom=CP["larkspur"]["october_test"][f"Oct {yr}"]["headroom"]["v"])
    totals = {y: {k: sum(qrows[q][k] for q in QS if q.startswith(y)) for k in ("revenue", "lost_contribution", "service_credits", "stock_written_off", "insurance", "ebitda", "gonzales_cases_k")}
              for y in ("FY2027", "FY2028")}
    return dict(retailers_delisting=PATHS[path], share_of_gonzales_revenue=share, quarters=qrows, larkspur=led, october_tests=octs, years=totals,
                min_commit_shortfall_k={y: max(0.0, REC["min_commit_k"] - totals[y]["gonzales_cases_k"]) for y in ("FY2027", "FY2028")})

RES = {p: build(p) for p in PATHS}

# ---------------------------------------------------------------- second-way check (closed form)
lost_total = sum(unmet)
closed_lost_days = A["days_down"] - (REC["buffer_days"] - REC["staged_days"])   # cap 1.0: shortage runs from day 13 to restart
lak_share = 160 * 0.6 / 312
closed_lak_fy28 = lak_share * sum(g_rev[f"FY2028 Q{n}"] for n in (2, 3, 4)) * cm["FY2028 Q2"] + lak_share * g_rev["FY2028 Q1"] * 31 / qdays("FY2028 Q1") * cm["FY2028 Q1"]
model_lak_fy28 = -RES["unexpected"]["years"]["FY2028"]["lost_contribution"] + RES["expected"]["years"]["FY2028"]["lost_contribution"]
CHECK = [dict(item="Days of Gonzales demand lost", main=round(lost_total, 2), check=float(closed_lost_days)),
         dict(item="Lakemont delisting, FY2028 contribution lost $M", main=round(model_lak_fy28, 2), check=round(closed_lak_fy28, 2))]
for c in CHECK: c["agree"] = abs(c["main"] - c["check"]) < 0.05
assert all(c["agree"] for c in CHECK), CHECK

# ---------------------------------------------------------------- write
r1 = lambda x: round(x, 2)
def clean(o):
    if isinstance(o, float): return r1(o)
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    return o

ASSUME = [
    ("Flood dated 12 August 2027, lines down 105 days (restart 25 November)", "Week 3 S2 date and the midpoint of its 60-150 day range; the co-packer would know"),
    ("No spare capacity after restart: the buffer is not rebuilt in the expected path", "Central projection has Gonzales full from Q2 FY2027"),
    ("Staged stock (14 days) written off in full at variable cost; tooling damage not priced", "Week 3 high basis; whether stock at a co-packer is insured is not in the summary"),
    ("Service credits on all Beverage invoices to the three retailers, scaled to central-projection Beverage revenue", "Week 3 high basis; SLA 6.2 says affected-PO invoices"),
    ("Contingent BI pays its $10.0M limit, settled and paid in Q1 FY2028, recognised in adjusted EBITDA then", "Limit and wait are RECORD; timing and add-back are ours; Treasurer and coverage counsel to confirm"),
    ("Lakemont decides at the February 2028 joint business plan review; Gonzales lines off shelf from 1 March 2028 for 12 months", "February review is RECORD (SLA Schedule 6-A); the decision and its length are ours"),
    ("Each retailer's Beverage buying is 60% Gonzales lines; Lakemont is 30.8% of Gonzales revenue", "Week 3 assumption; no customer-by-line split in the pack"),
    ("Fixed cost does not fall with lost volume; lost sales are not recovered elsewhere", "Conservative; the President, Beverage could say if other retailers would take the volume"),
    ("Cash: lost contribution after 25% tax, interest at 7% on the extra debt; stock write-off is non-cash", "Consistent with the central projection's cash rules"),
]
NOT_PRICED = ["Damage to Larkspur-owned filler tooling (value not in the pack)", "Expediting and alternative sourcing during the stop",
              "Shortfall against the 15.0M case minimum, invoiced at the Schedule 4 standby rate (rate not in the pack)",
              "Brand damage beyond the delisting retailer; the $18.5M launch investment at a retailer that drops the line",
              "Refinancing terms: the revolver matures in December 2027, one month after restart"]

doc = clean(dict(
    _about="Week 4 step 2: flood-to-delisting story against the central projection. Deltas are scenario minus central, $M; negative = worse. Built by scenarios/build_flood_delisting.py.",
    run=dict(run_id=RUN_ID, run_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), baseline_run="P-20261009-01",
             script="scenarios/build_flood_delisting.py", script_sha256=sha(__file__),
             inputs={"scenarios/central-projection.json": sha(HERE / "central-projection.json"), "scenarios/run_scenarios.py": sha(HERE / "run_scenarios.py")},
             note="Week 3 model imported for simulate(); no Week 3 file edited; run-log.csv not appended."),
    labels="Flood physical premise: Week 3 S2 (RECORD event, ASSUMPTION that water enters the plant). Every figure below is MODEL unless named in assumptions.",
    operating=dict(days_down=A["days_down"], restart=(d0 + dt.timedelta(days=A["days_down"])).isoformat(),
                   shelves_short_from=(d0 + dt.timedelta(days=sim["first_short"])).isoformat(), days_of_demand_lost=lost_total,
                   monthly_fill=fills, months_under_96_in_a_row=months_under, category_review_opens_after=review_month,
                   contingent_cover=cbi, contribution_lost_after_wait=after_wait),
    paths=RES, assumptions=[dict(value=a, why=w, label="ASSUMPTION") for a, w in ASSUME], not_priced=NOT_PRICED, check=CHECK,
))
(HERE / "flood-delisting.json").write_text(json.dumps(doc, indent=1))

# ---------------------------------------------------------------- markdown
f1 = lambda x: f"{(0.0 if abs(x) < 0.05 else x):,.1f}"
def tbl(h, rows): return "| " + " | ".join(h) + " |\n|" + "---|" * len(h) + "\n" + "".join("| " + " | ".join(r) + " |\n" for r in rows)
sq = lambda q: q.replace("FY20", "").replace(" ", "")
E, U, V = RES["expected"], RES["unexpected"], RES["variant_all_three"]
def qtab(res, title):
    Qr = res["quarters"]
    keys = [("revenue", "Revenue"), ("lost_contribution", "Contribution lost"), ("service_credits", "Service credits"), ("stock_written_off", "Staged stock written off"),
            ("insurance", "Contingent BI"), ("ebitda", "EBITDA effect"), ("cumulative_net_debt_change", "Net debt, cumulative +")]
    body = [[n] + [f1(Qr[q][k]) for q in QS] for k, n in keys]
    body.append(["Finished goods, days at quarter end"] + [f"{Qr[q]['fg_cover_days_end']:.0f}" for q in QS])
    body.append(["Larkspur leverage, quarter end"] + [f"{res['larkspur'][q]['leverage']:.2f}x" for q in QS])
    return f"**{title}** (change against central, $M)\n\n" + tbl([""] + [sq(q) for q in QS], body)

octrows = []
for name, res in (("Central", None), ("Expected: shelf comes back", E), ("Unexpected: Lakemont delists", U), ("Variant: all three delist", V)):
    if res is None:
        octrows.append([name] + [f"{CP['larkspur']['october_test'][k]['leverage']['v']:.2f}x / {f1(CP['larkspur']['october_test'][k]['headroom']['v'])}" for k in ("Oct 2027", "Oct 2028")])
    else:
        octrows.append([name] + [f"{res['october_tests'][k]['leverage']:.2f}x / {f1(res['october_tests'][k]['headroom'])}" for k in ("Oct 2027", "Oct 2028")])

op = doc["operating"]
md = f"""# Flood to delisting: Larkspur Week 4 scenario

Week 4 step 2 · run `{RUN_ID}` against central projection `P-20261009-01` · built by `scenarios/build_flood_delisting.py` · data in `flood-delisting.json`. Draft for Tripp's review. Figures are MODEL changes against the central projection, $M, unless labelled.

## The story

Water enters the Gonzales co-packer on 12 August 2027, a repeat of the August 2016 flood placed at the site (Week 3 S2: the rain is RECORD, water in the plant is a stress ASSUMPTION). Lines 2 and 3 stop for 105 days. The 14 days of stock staged there are lost, so shelves run short from {op['shelves_short_from']}. Category fill is under 96% for {op['months_under_96_in_a_row']} months in a row, so the category review under SLA 6.3 opens after {op['category_review_opens_after']}. The lines restart on {op['restart']}. The central projection's lines are already full, so restart meets demand but never rebuilds the buffer.

- **Expected reaction:** the review closes once fill recovers, and the shelf comes back.
- **Unexpected reaction:** Lakemont uses its February 2028 joint business plan review to drop the Gonzales lines from 1 March 2028. That is {U['share_of_gonzales_revenue']*100:.0f}% of Gonzales revenue.

## What it reveals

1. **No path breaches the covenant.** The October 2027 test, the closest point, reads {E['october_tests']['Oct 2027']['leverage']:.2f}x with ${f1(E['october_tests']['Oct 2027']['headroom'])}M of headroom; the central projection had {CP['larkspur']['october_test']['Oct 2027']['leverage']['v']:.2f}x. The delisting lands in FY2028, after a year of the central case paying down debt. Week 3's reading, that delisting plus the flood passes the covenant headroom, does not hold against the central projection. It depends on the central case's cash assumptions (dividends, interest, refinancing), which are not in the pack.
2. **The expected path is the more fragile one.** If the shelf comes back, the lines restart already full, so the buffer stays at 0 days through FY2028 and into the 2028 hurricane season. Any later stop, even a Francine, hits shelves on day one. Delisting frees capacity and rebuilds 27 days by Q2 FY2028.
3. **Delisting turns into a contract problem.** Gonzales volume falls to {U['years']['FY2028']['gonzales_cases_k']/1000:.1f}M cases in FY2028 if Lakemont delists ({V['years']['FY2028']['gonzales_cases_k']/1000:.1f}M if all three do), under the 15.0M case minimum. The shortfall is invoiced at the standby rate in Schedule 4, which is not in the pack. This is the unpriced line most likely to change the answer.
4. **Insurance pays $10.0M, against ${f1(-E['years']['FY2027']['ebitda'] + 0)}M of FY2027 EBITDA lost.** It arrives a quarter after the October test and a month after the revolver matures (December 2027).

## What it does

| | Expected | Unexpected (Lakemont) | Variant (all three) |
|---|---|---|---|
| EBITDA effect FY2027 | {f1(E['years']['FY2027']['ebitda'])} | {f1(U['years']['FY2027']['ebitda'])} | {f1(V['years']['FY2027']['ebitda'])} |
| EBITDA effect FY2028 | {f1(E['years']['FY2028']['ebitda'])} | {f1(U['years']['FY2028']['ebitda'])} | {f1(V['years']['FY2028']['ebitda'])} |
| Net debt added by end FY2028 | {f1(E['quarters']['FY2028 Q4']['cumulative_net_debt_change'])} | {f1(U['quarters']['FY2028 Q4']['cumulative_net_debt_change'])} | {f1(V['quarters']['FY2028 Q4']['cumulative_net_debt_change'])} |
| Gonzales cases FY2028 vs 15.0M minimum, k | {E['years']['FY2028']['gonzales_cases_k']:,.0f} | {U['years']['FY2028']['gonzales_cases_k']:,.0f} | {V['years']['FY2028']['gonzales_cases_k']:,.0f} |
| Finished goods at end FY2028, days | {E['quarters']['FY2028 Q4']['fg_cover_days_end']:.0f} | {U['quarters']['FY2028 Q4']['fg_cover_days_end']:.0f} | {V['quarters']['FY2028 Q4']['fg_cover_days_end']:.0f} |

October covenant tests (leverage / EBITDA headroom before 3.50x, $M):

{tbl(["Path", "Oct 2027", "Oct 2028"], octrows)}
## By quarter

{qtab(E, "Expected: the shelf comes back")}
{qtab(U, "Unexpected: Lakemont delists the Gonzales lines")}
## Assumptions (ours)

{"".join(f"- {a}. {w}." + chr(10) for a, w in ASSUME)}
## Not priced

{"".join(f"- {n}" + chr(10) for n in NOT_PRICED)}
## Check

{"; ".join(f"{c['item']}: {c['main']} vs {c['check']}" for c in CHECK)}. Both agree.
"""
(HERE / "flood-delisting.md").write_text(md)
print(RUN_ID, "review after", review_month, "| cbi", round(cbi, 1), "| lost days", round(lost_total, 1))
for p, r in RES.items():
    print(p, {y: round(v["ebitda"], 1) for y, v in r["years"].items()}, {k: (round(v["leverage"], 2), round(v["headroom"], 1)) for k, v in r["october_tests"].items()},
          "cases28", round(r["years"]["FY2028"]["gonzales_cases_k"]), "nd+", round(r["quarters"]["FY2028 Q4"]["cumulative_net_debt_change"], 1))
