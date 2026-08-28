# Runbook: Postgres

## Symptoms
- Slow queries / timeouts
- Connection pool exhausted
- App errors mentioning database locks

## Checks
1. Check disk space: `df -h`
2. Look at active queries: `SELECT * FROM pg_stat_activity;`
3. Look for blocking locks.
4. Confirm postgres status is RUNNING.

## Fix
1. Kill long idle transactions only if approved.
2. Free disk if nearly full (logs, temp files).
3. Restart postgres ONLY as a last resort and with approval.

## Escalate
Any production restart needs human approval. Page DBA on-call for lock storms.
