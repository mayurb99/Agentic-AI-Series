# Runbook: Redis

## Symptoms
- Cache misses spike
- Celery / apps report broker connection refused
- Service status shows redis STOPPED

## Checks
1. Check memory pressure: `free -h`
2. Confirm redis process: `systemctl status redis`
3. Tail redis log for OOM or RDB errors.

## Fix
1. Free memory if the host is under pressure.
2. Restart: `systemctl restart redis`
3. Confirm clients reconnect before closing the ticket.

## Escalate
If Redis OOMs again within 15 minutes, page platform on-call.
