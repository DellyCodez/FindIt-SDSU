# Phase 1 presentation — 8-minute plan

**Total classroom slot:** 8 minutes of presentation + 2 minutes for Q&A. All members should contribute meaningfully; exact speaking times can be adjusted to be equitable.

| Elapsed | Speaker | Segment |
| --- | --- | --- |
| 0:00–2:35 | Samuel | The campus problem, target users, product idea, navigation and proposed value |
| 2:35–5:10 | Andy | ER diagram, table relationships, normalization, SQL operations, transaction/constraint design |
| 5:10–8:00 | Alexander | Live walkthrough: report → search → claim → review; what works, what's next |

This is an **outline**, not a claim that the software is complete.

## Recommended slide sequence

1. The problem and why a consolidated workflow matters.
2. Users, scope and main product journey.
3. ER diagram and relational design.
4. Database operations, SQL joins, constraints and claim transaction.
5. Live product demonstration (or short local fallback recording).
6. Test findings, contribution summary, limitations and next phase.

## Demo checklist

- [ ] Use fully fictional seeded records.
- [ ] Run through the same end-to-end steps twice before presenting.
- [ ] Confirm the local server and database actually start after reboot.
- [ ] Open key pages in browser tabs as a recovery measure.
- [ ] Have a recorded backup if local networking or projection fails.
- [ ] Do not rely on `localhost` as the URL classmates will use from another device.
- [ ] Reserve the last few seconds for clearly describing incomplete areas.

## Likely Q&A

**How are categories and locations represented?** Explain foreign keys rather than duplicated text.

**What prevents duplicate returns?** Describe the claim transaction and database invariant.

**How would it scale to actual campus use?** Talk about moderation, authentication, privacy, hosting and institutional approval as future work.

**Where did AI help?** Refer to the truthful AI-use log and explain what the team checked and modified.

**How will you evaluate it?** Show tested SQL queries, seed size, results and any measured query-plan comparison.
