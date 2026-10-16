# Gazete veri deposu V1

This is an **operational SQLite builder**, not a deployed production database.

- `database/schema.sql`: normalized tables for sources, intake, entities, events, evidence, stories and image assets.
- `scripts/build_editorial_db.py`: imports source registry and triaged RSS records into SQLite, idempotently.
- `.github/workflows/editorial-data.yml`: creates a downloadable SQLite snapshot as a GitHub Actions artifact following successful RSS workflow or on manual trigger.
- RSS items remain **unverified leads**. No story is automatically approved or published.
- The generated database is **not committed to the public repository**.
- A workflow_run may race with other commits; this snapshot uses the current main branch when it runs.
- GitHub Actions execution and real feed ingestion remain unverified until the first successful run.

**Next production step:** private persistent database (e.g., PostgreSQL) with editorial authentication, incremental sync, audit trail and backups. Do not put database credentials into public repo files.
