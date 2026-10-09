# Response A2: a second aseptic site

Week 4 step 3 · run `P-20261009-03` against `P-20261009-01` (central) and `P-20261009-02` (flood to delisting) · built by `scenarios/build_a2_second_site.py` · data in `a2-second-site.json`. Draft for Tripp's review. Results are MODEL; the cost and site inputs are ASSUMPTIONS because the pack has neither.

**A2 as tested:** decide by 15 November 2026 and qualify a second aseptic co-packer, the 6 to 9 months Art. 14.2 records. From the day it is saleable, it fills whatever volume sits above Gonzales's 15.0M-case minimum, up to 4.0M cases a year (about 21%). Gonzales is never pushed under its minimum, and it gains the spare capacity it lacks in the central case.

## The answer, story by story

- **Central:** With no climate event, choosing A2 costs $5.4M of EBITDA over FY2027-28 ($3.5M capex on top), because Larkspur pays to qualify a site and a 4% premium on the 4.0M cases it moves; in return Gonzales gets about 21% spare capacity, which the central case does not have.
- **Expected:** Under the flood with the shelf coming back, choosing A2 (qualified by mid-August) roughly breaks even on FY2027-28 EBITDA (-0.2M) but starts the 2028 hurricane season with 27 days of stock instead of 0, because the second site keeps filling about a fifth of the lines while Gonzales is down and the freed capacity rebuilds the buffer after restart. If an Ida-sized stop then hit in late August 2028, that buffer is the difference between $6.9M of contribution lost with empty shelves from day one, and $0.0M. A2 does not stop the category review: fill stays under 96% for 4 months.
- **Unexpected:** Under the flood with Lakemont delisting, choosing A2 improves FY2027-28 EBITDA by $1.6M, because the shorter shortage in FY2027 roughly pays for the site; it does nothing for the delisting itself, which A2 does not prevent, or for the shortfall against the Gonzales minimum, which is the same with or without it.
- **Timing:** Timing decides the money: qualified by May, A2 improves FY2027-28 EBITDA by $3.5M in the expected path; if the decision slips to February and the site is ready in mid-November, it costs a net $4.4M of FY2027-28 EBITDA.
- **What A2 cannot do:** To keep category fill at 96% with Gonzales down, the second site would need about 93% of the Gonzales lines' volume, close to full dual sourcing. Sized to the minimum-commitment headroom, A2 cannot prevent a category review; it limits the damage and rebuilds the buffer.

## Results (EBITDA change against the central projection, $M)

| Story | Response | FY2027 | FY2028 | Oct 2027 test | Oct 2028 test | Stock days on 1 Jun 2028 | Category review |
|---|---|---|---|---|---|---|---|
| Central (no event) | No A2 | +0.0 | +0.0 | 2.49x | 1.86x | 27 | no |
|  | A2, 6 months | -3.8 | -2.1 | 2.54x | 1.90x | 27 | no |
|  | A2, 9 months | -3.3 | -2.1 | 2.53x | 1.90x | 27 | no |
|  | A2, decision slips to mid-February | -2.8 | -2.1 | 2.53x | 1.89x | 27 | no |
| Flood, shelf comes back | No A2 | -37.3 | +10.0 | 2.70x | 1.93x | 0 | yes |
|  | A2, 6 months | -31.7 | +7.9 | 2.68x | 1.93x | 27 | yes |
|  | A2, 9 months | -35.4 | +7.9 | 2.72x | 1.94x | 27 | yes |
|  | A2, decision slips to mid-February | -39.6 | +7.9 | 2.74x | 1.96x | 27 | yes |
| Flood, Lakemont delists | No A2 | -37.3 | -16.2 | 2.70x | 2.09x | 27 | yes |
|  | A2, 6 months | -31.7 | -16.5 | 2.68x | 2.08x | 27 | yes |
|  | A2, 9 months | -35.4 | -16.5 | 2.72x | 2.08x | 27 | yes |
|  | A2, decision slips to mid-February | -39.6 | -16.5 | 2.74x | 2.10x | 27 | yes |

## Sensitivities (flood with the shelf back, A2 at 9 months)

| Change | FY2027 | FY2028 | Review | Stock days 1 Jun 2028 |
|---|---|---|---|---|
| Surge: second site lifts output 50% while Gonzales is down | -32.7 | +7.9 | yes | 27 |
| Premium 8% on moved volume, not 4% | -36.2 | +5.7 | yes | 27 |
| One-time cost doubles ($5.0M opex, $7.0M capex) | -37.9 | +7.9 | yes | 27 |

## Assumptions (ours)

- Decision 15 November 2026; saleable after 6 or 9 months (base 9), or 15 November 2027 if the decision slips three months. Art. 14.2 records 6-9 months for the last line at the same facility; a new site could take longer.
- Volume moved: what is above Gonzales's 15.0M-case minimum, at most 4.0M cases a year (about 21%). Keeps Gonzales at its minimum so no shortfall charge; the candidate site's capacity is not in the pack.
- One-time cost $2.5M expensed and $3.5M capex, in FY2027 H1. Not in the pack (Week 3 gap: 'cost and candidate sites'); capex stays under the $85.0M covenant cap.
- Running premium 4% of variable cost on moved volume. Smaller runs and freight to Romeoville; not in the pack.
- No surge at the second site after a Gonzales stop (sensitivity at +50%). Its spare capacity is unknown.
- Second-site stock is not lost in the flood; staged stock at Gonzales is lost in proportion to its share. Different site, different flood exposure; the candidate site is unknown.
- After a delisting all remaining volume returns to Gonzales, so the premium stops; no second-site minimum. Contract terms for a second site are not known.

## Check

Days lost with no second site: this model vs Week 3 simulate(): 92.0 vs 92.0; expected FY2027 EBITDA without A2: this model vs P-20261009-02: -37.33 vs -37.33; expected FY2028 EBITDA without A2: this model vs P-20261009-02: 10.0 vs 10.0; unexpected FY2027 EBITDA without A2: this model vs P-20261009-02: -37.33 vs -37.33; unexpected FY2028 EBITDA without A2: this model vs P-20261009-02: -16.18 vs -16.18. All agree.
