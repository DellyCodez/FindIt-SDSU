# Reproducible database evaluation

Run `.venv/bin/python -m database.evaluate` from the repository root
(or `.\.venv\Scripts\python.exe -m database.evaluate` in Windows PowerShell).
The script creates and deletes a **temporary SQLite database**. It never opens
`instance/findit.sqlite3`. It uses a fixed random seed, 4,800 synthetic
background reports, seven curated lost/found pairs, and one deliberately
incompatible earbuds decoy (4,815 reports total).

## Queries and method

The script runs a JOIN across items, categories, and locations; a location
`GROUP BY` with `COUNT` and conditional `SUM`; and the bounded candidate
lookup used by Possible Matches. That lookup filters opposite kind, Open
status, category, compatible or unknown stored item type, and date range.
Python then checks known type, color, brand, and model conflicts and ranks
distinctive public details. A claim check exercises SQLite's one-approved
claim rule and automatic rejection of competing pending claims.

`CANDIDATE_SQL` in [database/evaluate.py](../database/evaluate.py) runs with
`INDEXED BY idx_items_match_candidates` and `NOT INDEXED`.
`EXPLAIN QUERY PLAN` records the chosen paths. Each timing is the median of
200 warm-cache executions after 12 warmups. It measures the SQL candidate
query in this container, not web page latency or complete ranking time.

## Observed run

One run in the cloud workspace used Python 3.12 and SQLite 3.53.1:

| Check | Result |
| --- | --- |
| Reports in temporary database | 4,815 |
| Foreign-key violations | 0 |
| JOIN example | `Red thermos with yellow star` → Drinkware, Library |
| Aggregate example | Arts and Letters: 711 reports, 365 found |
| Indexed candidate plan | `SEARCH i USING INDEX idx_items_match_candidates` |
| Forced scan plan | `SCAN i`; temporary B-tree for ordering |
| Indexed candidate query, median of 200 | 0.065 ms |
| Forced scan, median of 200 | 0.334 ms |
| Curated pairs retrieved in top three | 7/7 |
| Known incompatible iPhone/earbuds decoy | Excluded |
| Claim consistency | Returned item, competing claim Rejected, second approval blocked |

These are results from one synthetic run; timings vary by machine and cache.
The curated pairs and decoy are known cases, **not** a real-world estimate of
precision or recall. Most background reports lack structured attributes, so
the query benchmark mainly measures candidate lookup. Similar items, wrong
categories, incomplete descriptions, and the 45-day window can still produce
false leads or miss real ones. Andy's independent QA, ER diagram, and separate
SQL checks remain team deliverables.
