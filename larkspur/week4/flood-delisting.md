# Flood to delisting: Larkspur Week 4 scenario

Week 4 step 2 · run `P-20261009-02` against central projection `P-20261009-01` · built by `scenarios/build_flood_delisting.py` · data in `flood-delisting.json`. Draft for Tripp's review. Figures are MODEL changes against the central projection, $M, unless labelled.

## The story

Water enters the Gonzales co-packer on 12 August 2027, a repeat of the August 2016 flood placed at the site (Week 3 S2: the rain is RECORD, water in the plant is a stress ASSUMPTION). Lines 2 and 3 stop for 105 days. The 14 days of stock staged there are lost, so shelves run short from 2027-08-25. Category fill is under 96% for 4 months in a row, so the category review under SLA 6.3 opens after 2027-10. The lines restart on 2027-11-25. The central projection's lines are already full, so restart meets demand but never rebuilds the buffer.

- **Expected reaction:** the review closes once fill recovers, and the shelf comes back.
- **Unexpected reaction:** Lakemont uses its February 2028 joint business plan review to drop the Gonzales lines from 1 March 2028. That is 31% of Gonzales revenue.

## What it reveals

1. **No path breaches the covenant.** The October 2027 test, the closest point, reads 2.70x with $65.2M of headroom; the central projection had 2.49x. The delisting lands in FY2028, after a year of the central case paying down debt. Week 3's reading, that delisting plus the flood passes the covenant headroom, does not hold against the central projection. It depends on the central case's cash assumptions (dividends, interest, refinancing), which are not in the pack.
2. **The expected path is the more fragile one.** If the shelf comes back, the lines restart already full, so the buffer stays at 0 days through FY2028 and into the 2028 hurricane season. Any later stop, even a Francine, hits shelves on day one. Delisting frees capacity and rebuilds 27 days by Q2 FY2028.
3. **Delisting turns into a contract problem.** Gonzales volume falls to 14.1M cases in FY2028 if Lakemont delists (10.3M if all three do), under the 15.0M case minimum. The shortfall is invoiced at the standby rate in Schedule 4, which is not in the pack. This is the unpriced line most likely to change the answer.
4. **Insurance pays $10.0M, against $37.3M of FY2027 EBITDA lost.** It arrives a quarter after the October test and a month after the revolver matures (December 2027).

## What it does

| | Expected | Unexpected (Lakemont) | Variant (all three) |
|---|---|---|---|
| EBITDA effect FY2027 | -37.3 | -37.3 | -37.3 |
| EBITDA effect FY2028 | 10.0 | -16.2 | -36.6 |
| Net debt added by end FY2028 | 11.8 | 31.7 | 47.3 |
| Gonzales cases FY2028 vs 15.0M minimum, k | 19,000 | 14,117 | 10,303 |
| Finished goods at end FY2028, days | 0 | 27 | 27 |

October covenant tests (leverage / EBITDA headroom before 3.50x, $M):

| Path | Oct 2027 | Oct 2028 |
|---|---|---|
| Central | 2.49x / 88.2 | 1.86x / 160.1 |
| Expected: shelf comes back | 2.70x / 65.2 | 1.93x / 150.6 |
| Unexpected: Lakemont delists | 2.70x / 65.2 | 2.09x / 128.3 |
| Variant: all three delist | 2.70x / 65.2 | 2.22x / 110.9 |

## By quarter

**Expected: the shelf comes back** (change against central, $M)

|  | 27Q1 | 27Q2 | 27Q3 | 27Q4 | 28Q1 | 28Q2 | 28Q3 | 28Q4 |
|---|---|---|---|---|---|---|---|---|
| Revenue | 0.0 | 0.0 | -35.2 | -52.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| Contribution lost | 0.0 | 0.0 | -10.0 | -14.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| Service credits | 0.0 | 0.0 | -1.7 | -1.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| Staged stock written off | 0.0 | 0.0 | -9.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Contingent BI | 0.0 | 0.0 | 0.0 | 0.0 | 10.0 | 0.0 | 0.0 | 0.0 |
| EBITDA effect | 0.0 | 0.0 | -21.2 | -16.1 | 10.0 | 0.0 | 0.0 | 0.0 |
| Net debt, cumulative + | 0.0 | 0.0 | 6.4 | 18.6 | 11.3 | 11.5 | 11.6 | 11.8 |
| Finished goods, days at quarter end | 27 | 27 | 0 | 0 | 0 | 0 | 0 | 0 |
| Larkspur leverage, quarter end | 2.38x | 2.30x | 2.37x | 2.40x | 2.06x | 1.91x | 1.65x | 1.47x |

**Unexpected: Lakemont delists the Gonzales lines** (change against central, $M)

|  | 27Q1 | 27Q2 | 27Q3 | 27Q4 | 28Q1 | 28Q2 | 28Q3 | 28Q4 |
|---|---|---|---|---|---|---|---|---|
| Revenue | 0.0 | 0.0 | -35.2 | -52.3 | -9.4 | -27.5 | -27.5 | -27.5 |
| Contribution lost | 0.0 | 0.0 | -10.0 | -14.9 | -2.7 | -7.8 | -7.8 | -7.8 |
| Service credits | 0.0 | 0.0 | -1.7 | -1.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| Staged stock written off | 0.0 | 0.0 | -9.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Contingent BI | 0.0 | 0.0 | 0.0 | 0.0 | 10.0 | 0.0 | 0.0 | 0.0 |
| EBITDA effect | 0.0 | 0.0 | -21.2 | -16.1 | 7.3 | -7.8 | -7.8 | -7.8 |
| Net debt, cumulative + | 0.0 | 0.0 | 6.4 | 18.6 | 13.3 | 19.4 | 25.5 | 31.7 |
| Finished goods, days at quarter end | 27 | 27 | 0 | 0 | 13 | 27 | 27 | 27 |
| Larkspur leverage, quarter end | 2.38x | 2.30x | 2.37x | 2.40x | 2.09x | 2.00x | 1.79x | 1.65x |

## Assumptions (ours)

- Flood dated 12 August 2027, lines down 105 days (restart 25 November). Week 3 S2 date and the midpoint of its 60-150 day range; the co-packer would know.
- No spare capacity after restart: the buffer is not rebuilt in the expected path. Central projection has Gonzales full from Q2 FY2027.
- Staged stock (14 days) written off in full at variable cost; tooling damage not priced. Week 3 high basis; whether stock at a co-packer is insured is not in the summary.
- Service credits on all Beverage invoices to the three retailers, scaled to central-projection Beverage revenue. Week 3 high basis; SLA 6.2 says affected-PO invoices.
- Contingent BI pays its $10.0M limit, settled and paid in Q1 FY2028, recognised in adjusted EBITDA then. Limit and wait are RECORD; timing and add-back are ours; Treasurer and coverage counsel to confirm.
- Lakemont decides at the February 2028 joint business plan review; Gonzales lines off shelf from 1 March 2028 for 12 months. February review is RECORD (SLA Schedule 6-A); the decision and its length are ours.
- Each retailer's Beverage buying is 60% Gonzales lines; Lakemont is 30.8% of Gonzales revenue. Week 3 assumption; no customer-by-line split in the pack.
- Fixed cost does not fall with lost volume; lost sales are not recovered elsewhere. Conservative; the President, Beverage could say if other retailers would take the volume.
- Cash: lost contribution after 25% tax, interest at 7% on the extra debt; stock write-off is non-cash. Consistent with the central projection's cash rules.

## Not priced

- Damage to Larkspur-owned filler tooling (value not in the pack)
- Expediting and alternative sourcing during the stop
- Shortfall against the 15.0M case minimum, invoiced at the Schedule 4 standby rate (rate not in the pack)
- Brand damage beyond the delisting retailer; the $18.5M launch investment at a retailer that drops the line
- Refinancing terms: the revolver matures in December 2027, one month after restart

## Check

Days of Gonzales demand lost: 92.0 vs 92.0; Lakemont delisting, FY2028 contribution lost $M: 26.18 vs 26.18. Both agree.
