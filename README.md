# FindIt SDSU

A lost-and-found website we're building for our CS 514 database project at San Diego State University.

The idea is to give students one place to post items they've lost, report things they've found, and search for possible matches. We're starting with a small working version and will build on it throughout the semester.

## What we're building

For the first version, we want people to be able to:

- **Post a lost or found item** with a description, category, and campus location.
- **Browse and search reports** instead of going through individual posts.
- **View item details** and see whether an item is still available.
- **Submit a claim** when they think a found item belongs to them.
- **Review claims** through a simple demo page and mark returned items.

The claim process is the main feature we want to get right. A found item may have more than one claimant, but the system should only allow one approved claim.

## Database

We're planning to use five related tables: `users`, `items`, `categories`, `locations`, and `claims`. This lets us keep reports organized and track who submitted each item and claim.

See [Database design](docs/database.md) for the current plan.

## Tech stack

Our starting plan is **Python (Flask), SQLite, HTML, CSS, and JavaScript**. We're keeping the setup simple so we can focus on the database and a working website. We'll update this section if we change anything.

## Progress

**Phase 1 — getting started.** The database and website are being built. Setup instructions and screenshots will be added once there's a working version to run.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---

*This is a student project, not an official SDSU lost-and-found service.*
