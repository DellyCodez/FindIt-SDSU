# Database design

This is our starting design for FindIt SDSU. We may adjust fields as we build and test the website.

## Tables

| Table | Main information |
| --- | --- |
| `users` | ID, name, email |
| `categories` | ID, category name (electronics, keys, clothing, etc.) |
| `locations` | ID, campus location name |
| `items` | ID, reporter, category, location, title, description, lost/found type, status, date |
| `claims` | ID, found item, claimant, explanation, claim status, date |

## Relationships

- A user can report several items.
- Every item belongs to one category and one location.
- A user can submit claims for found items.
- One found item can have multiple claims, but only one should be approved.

We'll use primary and foreign keys to connect these tables instead of repeating category names or student details in every item record.

## Things we want to demonstrate

- Inserting, updating, deleting, and searching records with SQL.
- Joining items to their categories, locations, and reporters.
- Counting lost/found reports and claims with aggregate queries.
- Validating foreign keys and claim statuses.
- Approving a claim in a transaction so an item can't be returned to two people.

## Before coding against the schema

Alexander will implement the schema, exact columns and SQLite integration on `work/app`. Andy will review the schema, prepare fictional seed data and an ER diagram, and write database tests and sample queries on `work/database` using the approved column names. This page is still a design draft, not completed SQL code.
