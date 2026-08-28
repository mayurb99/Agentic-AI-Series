# Runbook: Nginx

## Symptoms
- 502 / 504 gateway errors
- Site unreachable
- Config reload fails

## Checks
1. Validate config: `nginx -t`
2. Read error log for upstream timeouts.
3. Confirm upstream app ports are listening.

## Fix
1. Fix any config errors reported by `nginx -t`.
2. Reload: `systemctl reload nginx`
3. If reload fails, restart: `systemctl restart nginx`

## Escalate
If errors continue after reload, check the upstream app health before paging network.
