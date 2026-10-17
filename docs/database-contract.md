# Database contract — proposed relational model

**Owner for design review:** Andy. **Integrator:** Alexander.

This is a proposed contract, not an implemented schema. Andy should review column names, foreign keys, CHECK constraints and indexes with Alexander before creating `database/schema.sql`. Once agreed, record any change here before altering application queries.

## Proposed entities

### users
`id` PK, `display_name`, `email` (fictional sample values only), `created_at`.

### categories
`id` PK, `name` UNIQUE. Example categories: Electronics, Keys, Bags, Clothing, Accessories.

### locations
`id` PK, `name` UNIQUE. Use general publicly known campus-style locations; avoid pretending this is an official SDSU location directory.

### items
`id` PK, `reporter_id` FK → users.id, `category_id` FK → categories.id, `location_id` FK → locations.id, `title`, `description`, `report_type` (`lost` or `found`), `status` (`open` or `returned`), `event_date`, `created_at`.

### claims
`id` PK, `item_id` FK → items.id, `claimant_id` FK → users.id, `private_details` (not public), `status` (`pending`, `approved`, `rejected`), `created_at`, `reviewed_at`.

## Relationships

- One user → many item reports.
- One category → many items.
- One location → many items.
- One found item → many claims.
- One user → many claims.
- At most one approved claim per found item. This is a database invariant, not only a UI rule.

## Proposed constraints

- `report_type IN ('lost','found')`; `status IN ('open','returned')`.
- Non-empty titles and valid required foreign keys.
- Claims are accepted only for found items; enforce in transactional application logic (a simple foreign key alone cannot enforce this).
- Approval must run atomically, verify item is open and a found report, approve the selected claim, reject competing pending claims, and mark item returned.
- For SQLite, a partial unique index on `claims(item_id)` where `status='approved'` can enforce the single-approval invariant. Confirm engine-specific syntax before implementation.
- Enable `PRAGMA foreign_keys = ON` on every SQLite connection.

## Proposed indexes

- `items(report_type, status, created_at)` for browse/filter.
- `items(category_id)` and `items(location_id)` for filtering.
- `claims(item_id, status)` for claim review.
- Unique constraint on approved claim per item as above.

Use `EXPLAIN QUERY PLAN` and measured test data to evaluate the value of indexes. Do not claim performance improvements until measurements exist.

## Query examples to plan

1. Join item reports to categories, locations and reporter display names.
2. Count open lost and found reports by type/category.
3. Find open found items with pending claims using JOIN/GROUP BY or EXISTS.
4. Verify an item has no approved claim before processing a review.
5. Use parameterized filtering for a search term and selected category/location.

## Team acceptance checkpoint

Before implementation, Andy and Alexander agree on: database engine, naming, date representation, sample-data ownership, transaction behavior and test fixtures. Samuel receives the final ER diagram and schema summary for the technical PDF.
