# FindIt SDSU — app build brief

This is the handoff for **Alexander's `work/app` branch**. The visual direction has already been approved. Build a polished, usable **student-project MVP** for the CS 514 Phase 1 demonstration. Start with the UI, then connect Andy's database once its schema is agreed.

**Read first:** `README.md`, `AGENTS.md`, `docs/database.md`, `docs/phase-1.md`. Do not change Andy's `work/database` or Samuel's `work/docs` branch. This is a build plan, **not a claim that these features exist yet**.

## Design direction — approved

We're aiming for a friendly, sophisticated lost-and-found site, **not** an admin dashboard and not a generic AI-generated landing page. Match the screenshot approved in our team planning conversation as closely as is practical. The owner can attach the visual reference to Codex. The description below is sufficient to start even without that image.

**Brand and appearance**
- Project name: **FindIt SDSU**. Create a simple original pin/locator mark (CSS or SVG). **Don't use SDSU's official university seal, logos, or claim endorsement.** A small footer should say: "Student project — not an official SDSU service."
- Use SDSU-inspired primary colors: dark red `#A6192E`, bright red `#D41736`, charcoal `#2D2828`, black `#000000`; white backgrounds, warm off-white/cream `#FAF8F5`, and restrained borders `#E7E2DD`. Reference: https://brand.sdsu.edu/identity/design-elements/colors .
- Spacious layout; editorial **serif for large hero/section headlines**, clean sans-serif for navigation, cards, and forms. Real hierarchy, comfortable spacing, rounded corners (not excessive), small purposeful shadows. Avoid glassmorphism, neon gradients, emoji icons, fake analytics panels, dashboards, excessive animation, and filler sections.
- Responsive at desktop (1440px), tablet (~768px), mobile (~375px). Proper contrast, visible focus, form labels, accessible navigation; respect reduced-motion preferences.

**Homepage composition (priority 1)**
1. Clean white navigation: original pin mark + FindIt SDSU wordmark left, Browse Items / How It Works / Report Item links, compact "Independent student project" on right. **Do not show a fake working Sign In button**; leave authentication out of Phase 1.
2. Large warm hero panel with left editorial headline on three lines: "Lost something on campus? Find it here." Make "Find it here." dark red. Eyebrow "A BETTER WAY TO RECONNECT"; subtitle about browsing reports and reuniting items. Two clear buttons: **Browse Items** (solid dark red) and **Report an Item** (outlined).
3. The reference mockup shows palm trees and recognizable campus architecture fading behind the **right side** of the hero. If we have a licensed image or one supplied by Alexander, use it with a restrained fade/overlay. **Do not hotlink random copyrighted campus photos**; an attractive CSS/typographic fallback must look good without a photo.
4. Wide search/filter bar below/overlapping hero: text query, segmented All/Lost/Found, category dropdown and location dropdown. It must really filter reports, not just look interactive.
5. "Recently reported" section with three-column desktop item cards and a **View all items** link. Each card: photo/placeholder with Lost or Found badge, item title, short description, location, time/date, View details. Example *fictional* fixtures: red water bottle, black earbuds, green backpack.
6. Small "How it works" section with three concise steps: Report / Search / Reconnect. Helpful footer with student-project disclaimer.

**Mobile layout:** Compact wordmark/hamburger navigation; stacked hero buttons; search input full width; filters wrap; one-column cards. No horizontal scrolling or overlapping panels.

**Product pages (priority 2)**
- `/` — homepage and recent reports.
- `/items` — browse all items, working query and lost/found/category/location filters, useful empty state.
- `/items/new` — report a lost or found item. Validate type, title, description, category, location, and date. Use a neutral item illustration when no photo is available. No login or file-upload infrastructure for Phase 1.
- `/items/<id>` — item detail showing title, report type/status, description, location, date, picture/placeholder. Show **Claim this item** for found reports only.
- `/items/<id>/claim` — short claim form for a found item, with contact/name and identifying explanation; never display claim evidence on the public item detail.
- `/review/claims` — a clearly labeled **demo-only reviewer screen** to view pending claims, approve or reject them, and mark returned items. It is **not secured with production authentication**; don't expose real student data or deploy this as a live claims workflow. Show the limitation.

Use normal links, forms and POST actions with success/error feedback. Search, create, claim and review actions must be functional when the database is connected. Don't implement email, campus SSO, AI matching, payments, messaging or production authentication in this phase.

## Stack and file boundaries

- Prefer **Python + Flask + SQLite + Jinja HTML templates + hand-written CSS + a little vanilla JS**. Don't replace it with Next.js/React or create a huge architecture.
- App work belongs in `app/`, `templates/` or `app/templates/`, `static/` or `app/static/`, `run.py` and `requirements.txt`. Pick one consistent structure.
- Database schema, seeds, SQL query documentation and database tests belong to Andy in `database/` and `tests/`. **Do not invent a competing permanent schema, rename Andy's columns, or overwrite his files.**
- Discuss a minimal data interface with Andy before implementing SQL-backed routes: `list_items(filters)`, `get_item(id)`, `create_item(data)`, `submit_claim(item_id, data)`, `list_pending_claims()`, `review_claim(id, action)`. Adjust to agreed schema; don't force an API on him.
- Make `PRAGMA foreign_keys = ON` part of each SQLite connection when integration is ready. Review/approval must use a transaction, prevent approval of two claims on one found item, and keep claim explanations private.
- For **UI development before the real schema arrives**, use a clearly named in-memory/demo fixture list in the application layer, **not a second SQL schema**. After Andy's SQL is available, swap the fixture layer for the actual SQLite interface. Don't pretend in-memory fixtures persist.
- Use only invented demo names/content. Don't commit a local `.db`, `.env`, credentials, or private student details.

## Build sequence — work through this in order

**Stage A: Make the site look right and run locally**
- Create the minimal Flask skeleton and installable dependencies.
- Implement desktop/mobile navigation, homepage, search/filter controls, item cards and footer matching the visual reference.
- Implement browse, report, item detail, claim and reviewer templates with helpful demo fixtures. Make the UI cohesive and actually clickable.
- Run it, inspect layouts at desktop and mobile widths, fix broken paths and console/server errors.

**Stage B: Make it a working database-backed demonstration**
- Check whether Andy's agreed `database/schema.sql` exists. If not, request the schema/column names before making dependent SQL changes. **Don't quietly replace his work**.
- Add the SQLite connection/data access layer compatible with Andy's schema. Make search, forms, claims and the demo reviewer flow persist.
- Verify with fictional seed data and a clean, repeatable local setup. Handle invalid IDs and invalid forms gracefully.
- Coordinate branch integration through a reviewed pull request. If blocked by unavailable schema, clearly identify the blocker and keep the UI demonstrable without inventing persistence.

**Stage C: Proof and handoff**
- Run local app and any available tests; show actual results, not claims.
- Provide a concise setup section in README once commands have been tested: create venv, install dependencies, initialize/seed DB, start Flask.
- Provide Samuel with real screenshots (desktop homepage, browse/search, report form, item details, claim/review), what works, and the exact local run/demo sequence.
- Keep future enhancements (auth/real campus integration/uploads) clearly labeled as future work.

## Definition of done — app

- [ ] A teammate can install and launch the Flask app from documented commands.
- [ ] Home looks close to the approved FindIt mockup at desktop and mobile widths.
- [ ] Buttons, navigation, filters and item cards work; there are no dead/demo-looking controls.
- [ ] Lost/found report form validates required fields.
- [ ] Users can open item details and submit a claim on a found item.
- [ ] Local-only review flow can approve/reject a claim, without exposing private evidence on public pages.
- [ ] After Andy's schema is integrated, records really persist in SQLite and a second claim can't be approved for the same found item.
- [ ] A basic test or repeatable manual demo verifies report → search → claim → review; note honestly what ran.
- [ ] Responsive CSS, alt text/accessible labels and useful empty/error states are present.
- [ ] Code is on `work/app`; no unauthorized push to `main`.

## Monday Phase 1 priority

The TA clarified Phase 1 is a **proof of concept**; the database is not required to be final at this presentation. Prioritize an attractive, runnable, understandable demo and real evidence for Samuel's website/presentation. Keep going toward full database integration if time allows, but don't jeopardize the working demo by rushing a conflicting schema.
