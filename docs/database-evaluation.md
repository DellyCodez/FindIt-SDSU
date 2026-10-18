# Reproducible database evaluation

Run `.venv/bin/python -m database.evaluate` from the repository root (or
`.\.venv\Scripts\python.exe -m database.evaluate` in Windows PowerShell).
The script creates and deletes a **temporary SQLite database**. It never opens
the normal `instance/findit.sqlite3` file. It uses a fixed random seed, 4,800
synthetic reports and six curated lost/found pairs (4,812 reports total).

## Representative SQL operations

The script runs these against the temporary database:

- A filtered JOIN of `items`, `categories`, and `locations` to list recent found
  Drinkware reports with their category and location names.
- A `GROUP BY` location query with `COUNT(*)` and conditional `SUM(...)` to
  count all reports and found reports by place.
- A candidate search over opposite report type, `Open` status, category, and
  date range. This is the lookup used by Possible Matches before Python scores
  public keywords and location.
- A claim approval that updates the item and competing claims within SQLite's
  transaction and trigger rules.

The exact SQL is in [`database/evaluate.py`](../database/evaluate.py) as
`JOIN_SQL`, `AGGREGATE_SQL`, and `CANDIDATE_SQL`. For the performance comparison,
the same candidate query runs once with `INDEXED BY idx_items_match_candidates`
and once with `NOT INDEXED`. `EXPLAIN QUERY PLAN` confirms which access path
SQLite chose. Each timing is the median of 200 warm-cache executions after 12
warmup executions; it is query execution time in this container, not page-load
latency.

## Observed run

One measured run on 2026-10-18 in the cloud workspace used Python 3.12 and SQLite 3.53.1:

| Check | Result |
| --- | --- |
| Reports in temporary database | 4,812 |
| Foreign-key violations | 0 |
| JOIN example | `Red thermos with yellow star` → Drinkware, Library |
| Aggregate example | Arts and Letters: 711 reports, 365 found |
| Indexed candidate plan | `SEARCH i USING COVERING INDEX idx_items_match_candidates` |
| Forced scan plan | `SCAN i`; temporary B-tree for ordering |
| Indexed candidate query, median of 200 | 0.051 ms |
| Forced scan, median of 200 | 0.401 ms |
| Structured curated pairs retrieved in top three | 6/6 |
| iPhone versus earbuds false positive | Excluded |
| Claim consistency | Returned item, competing claim Rejected, second approval blocked |

These figures are a single measured run on synthetic data after the structured
field migration. Timings vary by
machine and cache state. The six pairs check that the known examples are found;
they are **not** an estimate of real-world matching precision or recall. Similar
items, incorrect categories, incomplete descriptions, and the 45-day window
can cause false suggestions or missed matches. Andy's independent QA, ER
diagram, and separate SQL checks remain his team's deliverables.
