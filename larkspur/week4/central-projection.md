# Larkspur central projection, FY2027–FY2028 (no climate event)

Week 4 step 1 · run `P-20261009-01` · built by `scenarios/build_central_projection.py` · full labelled data in `central-projection.json`. Draft for Tripp's review. FY2025 = RECORD (pack); FY2026 = bridge estimate; every projected figure is MODEL built on the ASSUMPTIONS listed below. $M unless stated.

## What the projection assumes

Lakemont, Fairmount, Callahan and every other customer keep ordering at FY2025 patterns, with Beverage prices up 2% a year and no listing lost. River Parish Aseptic Packaging fills Lines 2 and 3 every week with no force-majeure stop, and San Antonio and Holland run without interruption. The March 2027 Prairie Clover functional-line launch goes ahead on 1 March as the board approved, spending the $18.5M and lifting the functional line about 40%, in step with the berry plan. Capacity meets demand, but only because core Gonzales volumes stay flat: with the launch the lines are 99% full in FY2027 and full in FY2028, so 27 days of finished goods is held and no sale is lost. Customers pay on terms and working capital grows in line with sales, so free cash flow pays down net debt every quarter and both credit facilities are refinanced on current terms as they mature. The October revolver peak repeats the FY2025 swing, so the covenant is tested each October against net debt about $93M above the quarter-end figure.

## FY2025 reconciles to the pack

| Item | Pack | Model | OK | Source |
|---|---|---|---|---|
| Beverage revenue, sum of seven lines | 520.0 | 520.0 | yes | division-pnl.csv Beverage fy2025_revenue_usd_m |
| Gonzales lines revenue (BV-03 to BV-06) | 312.0 | 312.0 | yes | Week 3 run R-20261001-02 records.gonzales_rev |
| Gonzales lines contribution | 86.76 | 86.76 | yes | Week 3 run R-20261001-02 records.gonzales_contrib |
| Gonzales cases, thousand | 18,000.0 | 18,000.0 | yes | beverage-volume-by-line.csv; 95% of 19.0M rated |
| Beverage EBITDA | 67.6 | 67.6 | yes | division-pnl.csv (holds by construction: fixed cost is the balancing figure) |
| Larkspur revenue | 2,500.0 | 2,500.0 | yes | division-pnl.csv Total |
| Larkspur adjusted EBITDA | 297.7 | 297.7 | yes | division-pnl.csv Total; compliance certificate |
| Net debt: 900 + 45 + 18 - 129 | 834.0 | 834.0 | yes | credit agreement certificate |
| First-lien net leverage | 2.8 | 2.8 | yes | credit agreement certificate (2.8x) |
| Headroom to 3.50x at year-end net debt | 59.4 | 59.41 | yes | Week 3 scenario-set.json dependency facts |


Beverage EBITDA reconciles by construction: fixed cost ($81.2M) is the figure that makes recorded line margins meet the recorded $67.6M. Revenue, Gonzales contribution and the Larkspur totals reconcile independently.

## Beverage by quarter

| Gonzales lines (BV-03 to 06) | 25 | 26 | 27Q1 | 27Q2 | 27Q3 | 27Q4 | 28Q1 | 28Q2 | 28Q3 | 28Q4 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cases, k | 18,000 | 18,000 | 4,590 | 4,750 | 4,750 | 4,750 | 4,750 | 4,750 | 4,750 | 4,750 | 18,840 | 19,000 |
| Utilisation % | 95 | 95 | 97 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 99 | 100 |
| Revenue | 312.0 | 318.2 | 83.4 | 87.5 | 87.5 | 87.5 | 89.2 | 89.2 | 89.2 | 89.2 | 345.8 | 356.9 |
| Variable cost | 225.2 | 229.7 | 60.0 | 62.5 | 62.5 | 62.5 | 63.8 | 63.8 | 63.8 | 63.8 | 247.5 | 255.0 |
| Fixed cost | 48.7 | 50.2 | 24.0 | 17.5 | 15.7 | 12.9 | 13.3 | 13.3 | 13.3 | 13.3 | 70.2 | 53.2 |
| of which launch | 0.0 | 0.0 | 11.1 | 4.6 | 2.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 18.5 | 0.0 |
| EBITDA | 38.0 | 38.3 | -0.6 | 7.4 | 9.3 | 12.0 | 12.2 | 12.2 | 12.2 | 12.2 | 28.1 | 48.6 |
| FG on hand, k cases | 1,335 | 1,335 | 1,362 | 1,409 | 1,409 | 1,409 | 1,409 | 1,409 | 1,409 | 1,409 | 1,397 | 1,409 |
| FG on hand, $M | 16.7 | 17.0 | 17.8 | 18.5 | 18.5 | 18.5 | 18.9 | 18.9 | 18.9 | 18.9 | 18.4 | 18.9 |



| Other lines + Beverage total | 25 | 26 | 27Q1 | 27Q2 | 27Q3 | 27Q4 | 28Q1 | 28Q2 | 28Q3 | 28Q4 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Other lines revenue | 208.0 | 216.4 | 56.3 | 56.3 | 56.3 | 56.3 | 58.6 | 58.6 | 58.6 | 58.6 | 225.1 | 234.2 |
| Other lines EBITDA | 29.6 | 31.1 | 8.2 | 8.2 | 8.2 | 8.2 | 8.6 | 8.6 | 8.6 | 8.6 | 32.7 | 34.4 |
| Beverage revenue | 520.0 | 534.6 | 139.7 | 143.8 | 143.8 | 143.8 | 147.8 | 147.8 | 147.8 | 147.8 | 571.0 | 591.1 |
| Beverage variable cost | 371.2 | 381.6 | 99.5 | 102.0 | 102.0 | 102.0 | 104.8 | 104.8 | 104.8 | 104.8 | 405.5 | 419.4 |
| Beverage fixed cost | 81.2 | 83.6 | 32.6 | 26.2 | 24.3 | 21.5 | 22.2 | 22.2 | 22.2 | 22.2 | 104.7 | 88.7 |
| Beverage EBITDA | 67.6 | 69.4 | 7.6 | 15.6 | 17.4 | 20.2 | 20.8 | 20.8 | 20.8 | 20.8 | 60.8 | 83.0 |
| Beverage FG on hand, $M | 27.5 | 28.3 | 29.5 | 30.3 | 30.3 | 30.3 | 31.1 | 31.1 | 31.1 | 31.1 | 30.1 | 31.1 |


## Larkspur-wide net debt and leverage

| Larkspur | 25 | 26 | 27Q1 | 27Q2 | 27Q3 | 27Q4 | 28Q1 | 28Q2 | 28Q3 | 28Q4 | 27 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Adjusted EBITDA (period) | 297.7 | 309.7 | 70.3 | 78.4 | 80.2 | 83.0 | 86.3 | 86.3 | 86.3 | 86.3 | 311.9 | 345.2 |
| EBITDA, LTM | 297.7 | 309.7 | 302.7 | 303.6 | 306.3 | 311.9 | 327.8 | 335.8 | 341.9 | 345.2 | 311.9 | 345.2 |
| Net debt, period end | 834.0 | 740.3 | 721.7 | 696.8 | 670.3 | 641.3 | 609.1 | 576.4 | 543.3 | 509.8 | 641.3 | 509.8 |
| Leverage (3.50x covenant) | 2.80x | 2.39x | 2.38x | 2.30x | 2.19x | 2.06x | 1.86x | 1.72x | 1.59x | 1.48x | 2.06x | 1.48x |
| Headroom before 3.50x | 59.4 | 98.2 | 96.5 | 104.5 | 114.8 | 128.6 | 153.8 | 171.1 | 186.6 | 199.5 | 128.6 | 199.5 |


At the mid-October test (Q3-end net debt + $93M harvest build):


| Test | Net debt at test | LTM EBITDA | Leverage | Headroom |
|---|---|---|---|---|
| Oct 2025 | 927.0 | 297.7 | 3.11x | 32.8 |
| Oct 2027 | 763.3 | 306.3 | 2.49x | 88.3 |
| Oct 2028 | 636.3 | 341.9 | 1.86x | 160.1 |


## Assumptions (ours, to confirm)

- **price**: +2.0% a year price/mix on every Beverage line. FY2025 Beverage revenue grew 6.1% (RECORD); the price/volume split is not in the pack. Confirm: President, Beverage.
- **vol_other**: +2.0% a year volume at San Antonio and Holland. San Antonio capacity is not in the pack and the Line 3 expansion is deferred (board minutes item 4). Confirm: COO.
- **vol_gonz_core**: Flat volume on BV-03, BV-04, BV-06 (15.9M cases). Lines 2 and 3 run at 95%; with the launch, any core growth exceeds rated capacity (see sensitivity 1). Confirm: COO; President, Beverage.
- **launch**: Functional line (BV-05) launches 1 March 2027: 2,940k cases in FY2027 (+40% on FY2025), 3,100k in FY2028 (775k a quarter). Sized on the +40% berry procurement for FY2027 (logistics note, RECORD); the volume plan itself is missing. Confirm: President, Beverage.
- **margins**: FY2025 contribution margin by line held constant. Price assumed to pass through cost inflation; carton and resin pass through at cost +2% (co-pack schedules). Confirm: CFO.
- **fixed**: Beverage fixed cost $81.2M in FY2025 (balancing figure), +3% a year; 60% allocated to Gonzales lines by revenue. The pack has no fixed/variable split; contribution margins define variable cost. Confirm: CFO.
- **launch_cost**: $18.5M slotting and launch marketing (RECORD) is incremental to run-rate cost, all in FY2027, phased 60/25/15/0 by quarter, charged to Gonzales lines. Board approved it within the FY2027 plan; timing not stated. Confirm: President, Beverage.
- **seasonality**: Demand, costs and cash flow flat across quarters. Same as the Week 3 model; quarterly phasing not in the pack. Confirm: CFO.
- **fg**: Beverage finished goods held at 27 days of sales, 14 staged at Gonzales, valued at variable cost. Days are RECORD (logistics note); valuation basis is not in the pack. Confirm: Logistics; Controller.
- **other_divisions**: Ingredients +4.4% and Produce +3.8% revenue a year (FY2025 growth repeated), FY2025 margins held; corporate cost +3%. No plan figures in the pack. Confirm: CFO.
- **fy2026**: FY2026 built with the same rules (functional line flat); no FY2026 actuals are in the pack. Bridge year to FY2027. Confirm: CFO.
- **cash**: Capex $75M a year; D&A $75M; interest 7.0% on gross debt (net debt + $129M cash held); tax 25% of EBITDA less D&A and interest; dividends $20M; working capital 12% of revenue growth. Capex is FY2025 division capex $73M (RECORD) rounded up for ERP phase 2; the rest is not in the pack. Confirm: Treasurer; CFO.
- **refinance**: Revolver (matures Dec 2027) and Term Loan B (bullet June 2028) refinanced on current terms, no fees. Both maturities fall inside the projection; the pack has no refinancing plan. Confirm: Treasurer.
- **peak_build**: Net debt rises $93.0M from Q3-end to the mid-October test, as the FY2025 revolver swing ($45M to $138M peak) did. Peak usage is RECORD for FY2025 only. Confirm: Treasurer.
- **test_springs**: The covenant is treated as tested every October. FY2025 peak draw of $138M was 55% of the $250M revolver, above the 35% trigger; if free cash repays the revolver first, the test may not spring. Confirm: Treasurer.


## Sensitivities (MODEL)

- Gonzales core lines (BV-03, -04, -06) grow volume 2% a year instead of flat: FY2028 Gonzales demand 19.97M cases against 19.0M rated: 0.97M cases a year cannot be filled. 'Capacity meets demand' fails from FY2027.
- Launch reaches half the volume (+20% on FY2025, not +40%): Functional line about 420k cases a year lower; Beverage EBITDA about $4.1M a year lower in FY2028; Gonzales keeps ~0.6M cases of spare capacity.
- Beverage price/mix +1% a year instead of +2%: FY2028 Beverage EBITDA about $5.0M lower (margin held).
- Dividends $40M a year instead of $20M, or interest at 8% instead of 7%: Each adds roughly $20M and $7M (before tax) a year respectively to net debt; FY2028 year-end leverage moves by about 0.1x and 0.04x.


## Check

Recomputed a second way with closed-form annual arithmetic: FY2027 Gonzales revenue 345.829 vs 345.829; FY2027 other-lines revenue 225.146 vs 225.146; FY2027 Beverage EBITDA 60.84 vs 60.84; FY2027 Gonzales utilisation % 99.158 vs 99.158; FY2028 Gonzales utilisation % 100.0 vs 100.0. All agree.


## Missing from the pack

- FY2026 year-to-date actuals and the FY2027 plan (revenue, EBITDA, volume by line)
- Functional-line launch volume plan and slotting date (Week 3 gap, still open)
- Fixed and variable cost split for Beverage; finished-goods valuation basis
- San Antonio capacity and utilisation
- Interest rate actually paid (SOFR and swaps), cash tax, dividend amount, D&A
- Quarterly seasonality of revenue, EBITDA and working capital
- Refinancing plan for the December 2027 revolver and June 2028 term loan
- How the October covenant test measures net debt (point in time, quarter-end, or average)


## Flags for Tripp

1. Capacity: the central case only holds 'capacity meets demand' because we held Gonzales core volume flat. With the launch at +40%, Lines 2 and 3 run at 99.2% in FY2027 and 100% from Q2 FY2027 on. Spare capacity, the thing that rebuilt the buffer in the Week 3 run (1.0M cases a year), is gone in the central case. Every Week 4 scenario will recover more slowly than Week 3 showed.
2. Covenant headroom at the October test is smaller than the $59.4M Week 3 used. Week 3 measured headroom at year-end net debt; the test falls at the revolver peak. Adding the FY2025 swing ($93M) gives 3.11x and $32.8M of headroom for October 2025 (illustrative). This changes how close a scenario comes to breach. Week 3 files not edited; needs Tripp's call and the Treasurer's confirmation of the test mechanics.
3. Both credit facilities mature inside the window (revolver Dec 2027, term loan June 2028). The central case assumes routine refinancing; a climate loss landing in 2027 lands during that refinancing.
4. The $18.5M launch spend takes FY2027 Beverage EBITDA down even in the central case. Q1 FY2027 is the weakest quarter before any event.
5. Several assumptions move annual EBITDA by more than $5M (price/mix, launch volume, fixed-cost growth). Per cda-workflow.md these need Tripp's review before results are quoted.
