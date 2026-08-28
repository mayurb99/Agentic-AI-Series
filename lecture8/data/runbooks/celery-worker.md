# Runbook: Celery Worker

## Symptoms
- Queue depth grows
- Background jobs never finish
- Service status shows celery-worker STOPPED

## Checks
1. Confirm the broker is up (Redis or RabbitMQ).
2. Look for OOM kills: `dmesg | grep -i kill`
3. Check worker logs under `data/logs/celery-worker.log`

## Fix
1. Start the broker if it is down.
2. Restart the worker: `systemctl restart celery-worker`
3. Confirm one worker process is consuming tasks again.

## Escalate
If the worker dies again within 10 minutes, page the backend on-call.
