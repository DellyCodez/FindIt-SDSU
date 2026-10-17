# Security and privacy

FindIt SDSU is a classroom prototype, **not a production service**. Do not submit real lost-item claims, student IDs, addresses, phone numbers, passwords, serial numbers or private ownership evidence.

## Prototype safeguards

- Use fictional demo accounts and seeded records only.
- Do not show private claim evidence in public listings.
- Validate all user-entered data server-side and use parameterized SQL.
- Keep configuration secrets out of Git.
- Do not expose a publicly writable reviewer endpoint as an authenticated production workflow. A demo-only reviewer is not real authorization.
- Before any public deployment, implement authentication, role-based authorization, rate limiting, abuse reporting, audit logging, secure file uploads (if any), privacy notices and a data-retention plan.

## Reporting a concern

Please open a GitHub issue for ordinary, non-sensitive bugs. For a potential vulnerability that could expose information, contact the project owner privately instead of publishing exploit steps or personal data in an issue.

No claims of security certification, SDSU SSO support or institutional integration should be made without evidence and approval.
