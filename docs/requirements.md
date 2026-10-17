# Phase 1 requirements and acceptance criteria

**Status:** draft baseline, to be confirmed by the three contributors before implementation.

## Functional requirements

| ID | Feature | Acceptance criteria |
| --- | --- | --- |
| F-01 | Create item report | Demo reporter can enter title, description, lost/found type, category, location and date; a record is persisted; invalid input is rejected. |
| F-02 | Browse items | A visitor sees persisted reports in newest-first order, with an informative empty state. |
| F-03 | Search and filter | Keyword, type, category and location filters return only matching rows through real SQL queries. |
| F-04 | Item detail | One report shows its non-sensitive description, location, category, date and report status. |
| F-05 | Submit ownership claim | A demo user can claim a found item, including private evidence; the claim points to a valid user and item. |
| F-06 | Review claim | Demo reviewer can approve or reject a pending claim; approving one resolves the item and prevents a second approval. |
| F-07 | Dashboard summary | Counts of lost, found, returned and pending-claim records reflect actual database state. |
| F-08 | Seeded demo | A repeatable dataset of clearly fictional users, campus-style locations and items is available for evaluation. |

## Database requirements

- Separate user, category, location, item and claim entities with primary keys and foreign keys.
- Enforce type and status domains with database constraints.
- Use SELECT, INSERT, UPDATE, DELETE, joins and aggregate queries; show at least one relevant subquery if it improves the design.
- Apply appropriate indexes and describe the reasons for them.
- Review and approve a claim in one transaction; enforce at most one approved claim per found item.
- Show at least one deliberate example of normalization (e.g. reusable category/location tables).
- Record SQL behavior and test outcomes, not just UI screenshots.

## Experience and safety requirements

- Each input has a label and useful validation feedback.
- Keyboard access, visible focus and usable small-screen layouts should be considered.
- Public item listings never reveal private proof of ownership.
- Never use real student identities or contact information in the class demo.
- Any reviewer capability without actual authentication must be labeled **demo-only**.
- Distinguish sample data from real campus records.

## Scope control

Defer login, SSO, paid services, chat, image uploads, maps, machine-learning matching and notifications until the core flow works and is tested.

## Definition of done

A requirement is done only when its behavior has been demonstrated against persistent records, its important error states have been checked, and supporting test evidence exists. Mark anything else planned or incomplete in the presentation.
