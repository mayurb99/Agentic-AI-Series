# Runbook: Deploy Rollback

## Symptoms
- Error rate spike right after a release
- Canary health checks failing
- New version returns 5xx

## Checks
1. Confirm which version is live (deploy dashboard or `kubectl get deploy`).
2. Compare error rate before vs after deploy.
3. Check recent change ticket / PR.

## Fix
1. Pause further rollouts.
2. Roll back to the previous known-good version.
3. Verify error rate returns to baseline.
4. File an incident ticket with the bad version id.

## Escalate
If rollback fails or impact is customer-facing > 15 minutes, page incident commander.
