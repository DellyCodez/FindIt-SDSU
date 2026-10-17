# Product brief — FindIt SDSU

## One-sentence description

An independent campus lost-and-found platform that brings lost-item reports, found-item reports and ownership-claim review into one searchable workflow.

## The problem

Lost-item information is scattered across conversations, location-specific desks and informal posts. Students may not know where to look; people who find an item may not know how to report it; and there is no consistent record linking a found item to a possible owner.

This is the team's problem hypothesis, **not** a verified statement about the capabilities of SDSU's current services. Any real institutional proposal would begin with user interviews and campus stakeholder review.

## Who it is for

- **Person who lost an item:** searches by object, approximate location and category, then requests verification.
- **Person who found an item:** reports the item with enough description to make it searchable while withholding sensitive distinguishing details.
- **Reviewer / lost-and-found staff role:** inspects claim evidence privately and resolves each item's outcome. This role is only simulated for Phase 1.

## Core product journey

1. A finder reports a set of keys near a campus building.
2. The system stores the item, category, location and report metadata in related tables.
3. A student searches for missing keys and opens the listing.
4. The student files an ownership claim with details that are not public.
5. A demo reviewer approves a valid claim and the system closes competing claims consistently.

## Product principles

- **Search first:** reporting and browsing should be faster than filling out a long form.
- **Privacy by default:** protect identifying details and private ownership evidence.
- **Clear statuses:** lost, found, claimed and returned should not be conflated.
- **Accessible design:** readable contrast, keyboard navigation and clear form errors.
- **Traceable decisions:** database constraints, transactions and future audit trails matter more than visual gimmicks.

## Boundaries

**Phase 1:** working local prototype, fictional sample data, core relational workflows, basic moderation demo, documented schema and repeatable tests.

**Phase 2 candidates:** role-based access, real deployment, location-specific moderation, audit records, image uploads with safety checks, improved matching and performance measurements. None should be claimed as complete until implemented.

**Outside current scope:** SDSU single sign-on, integrations with campus systems, real item custody, automated identity verification, production notifications and official campus adoption.

## What success looks like

Phase 1 succeeds if the team can demonstrate the report → search → claim → review workflow end to end with persistent data, valid foreign keys, and a demonstrable single-approved-claim rule. Maintain evidence for tests and query behavior in the technical report.

Before claiming broader campus value, collect interviews and operational feedback from SDSU stakeholders with appropriate permission.

## Positioning and identity

FindIt SDSU is a proposed student-developed product. Use the name descriptively, not as evidence of university affiliation. Avoid official SDSU seals, unlicensed logos and a misleading campus-services appearance.
