# _devops_corpus.py
# Lecture 2 — shared data: 50 short DevOps "runbook" style knowledge-base
# entries, reused by demo 2 and demo 3.
#
# DevOps analogy: think of this as a tiny slice of an internal wiki / incident
# postmortem archive -- the kind of thing a new on-call engineer would search
# through at 3 AM. That is exactly the scenario demo 3 builds towards: instead
# of Ctrl+F-ing 50 wiki pages for the right keyword, you ask a question in
# plain English and semantic search finds the *meaning* match, not just the
# text match.
#
# Deliberately plain Python: a list of dicts. No database, no framework.

DEVOPS_DOCS = [
    {"id": "doc_01", "text": "The Kubernetes pod was killed by the OOM killer after memory usage exceeded its configured limit."},
    {"id": "doc_02", "text": "Increasing the container's memory request and limit in the deployment manifest resolved the repeated crash loop."},
    {"id": "doc_03", "text": "The root disk on the build server filled up because Docker images were never pruned, blocking new deployments."},
    {"id": "doc_04", "text": "Running a scheduled cron job to prune unused Docker images and old logs freed up disk space on the node."},
    {"id": "doc_05", "text": "The TLS certificate for the public API expired at midnight, causing every HTTPS request to fail with a handshake error."},
    {"id": "doc_06", "text": "Setting up automatic certificate renewal with Let's Encrypt and a 30-day expiry alert prevented future outages."},
    {"id": "doc_07", "text": "DNS resolution for the internal service name started failing after the CoreDNS pods were rescheduled to a new node."},
    {"id": "doc_08", "text": "Restarting the CoreDNS deployment and verifying the ConfigMap restored name resolution across the cluster."},
    {"id": "doc_09", "text": "A bad deployment introduced a null pointer exception, so the rollout was automatically rolled back to the previous stable version."},
    {"id": "doc_10", "text": "Configuring a readiness probe meant Kubernetes stopped routing traffic to pods before they were actually ready to serve requests."},
    {"id": "doc_11", "text": "The application entered a CrashLoopBackOff state because the startup script referenced an environment variable that was never set."},
    {"id": "doc_12", "text": "Adding the missing environment variable to the ConfigMap and redeploying fixed the crash loop immediately."},
    {"id": "doc_13", "text": "Users started seeing 502 Bad Gateway errors because the upstream service pool behind the load balancer had zero healthy backends."},
    {"id": "doc_14", "text": "The load balancer health check interval was too aggressive, marking healthy backends as down under normal load."},
    {"id": "doc_15", "text": "The database connection pool was exhausted because a long-running query held connections open far longer than expected."},
    {"id": "doc_16", "text": "Lowering the query timeout and adding a connection pool size alert prevented the database from being starved of connections."},
    {"id": "doc_17", "text": "CPU throttling started appearing on the metrics dashboard right after a Kubernetes CPU limit was set too close to average usage."},
    {"id": "doc_18", "text": "Raising the CPU limit and switching the workload to a burstable QoS class removed the throttling seen in the dashboards."},
    {"id": "doc_19", "text": "Log files on the application server grew unbounded overnight because logrotate was never configured for the new service."},
    {"id": "doc_20", "text": "Adding a logrotate configuration with daily rotation and compression stopped the disk from filling up with old logs."},
    {"id": "doc_21", "text": "The nightly backup job silently failed for three days because a credential used to authenticate to the storage bucket had expired."},
    {"id": "doc_22", "text": "Rotating the storage bucket credential and adding a Slack alert on backup job failure caught the next issue within minutes."},
    {"id": "doc_23", "text": "A secret stored in plaintext in the deployment YAML was flagged during a security audit of the cluster."},
    {"id": "doc_24", "text": "Migrating secrets into a dedicated secrets manager and mounting them as files removed all plaintext credentials from manifests."},
    {"id": "doc_25", "text": "A network partition between two availability zones caused half the cluster nodes to report as NotReady simultaneously."},
    {"id": "doc_26", "text": "Enabling multi-zone pod anti-affinity rules ensured a single zone failure no longer takes down every replica of a service."},
    {"id": "doc_27", "text": "The horizontal pod autoscaler failed to scale up during a traffic spike because the metrics server was not reporting CPU usage."},
    {"id": "doc_28", "text": "Reinstalling the metrics server and verifying its API availability restored autoscaling behavior during the next load test."},
    {"id": "doc_29", "text": "A container image pull failed in production because the image tag had been overwritten with a different build by mistake."},
    {"id": "doc_30", "text": "Switching to immutable image tags with a unique build hash prevented any future image from being silently replaced."},
    {"id": "doc_31", "text": "The CI pipeline started failing intermittently because parallel test jobs were writing to the same shared temporary directory."},
    {"id": "doc_32", "text": "Isolating each CI job's temporary directory using a unique build ID eliminated the flaky parallel test failures."},
    {"id": "doc_33", "text": "A canary deployment received a spike in error rates within the first five minutes, and the pipeline halted the rollout automatically."},
    {"id": "doc_34", "text": "Wiring the deployment pipeline to automatically halt on an error-rate threshold prevented a bad release from reaching every user."},
    {"id": "doc_35", "text": "Alert fatigue set in after the monitoring system fired the same low-priority warning hundreds of times in one night."},
    {"id": "doc_36", "text": "Grouping related alerts and adding a severity threshold cut the number of on-call pages by more than half."},
    {"id": "doc_37", "text": "A misconfigured firewall rule blocked outbound traffic from the application tier to the payment provider's API."},
    {"id": "doc_38", "text": "Adding an explicit egress rule for the payment provider's IP range restored outbound connectivity from the application tier."},
    {"id": "doc_39", "text": "The message queue consumer fell behind during a traffic surge, causing a growing backlog of unprocessed orders."},
    {"id": "doc_40", "text": "Scaling out the number of consumer replicas and tuning the batch size cleared the message queue backlog within an hour."},
    {"id": "doc_41", "text": "A stale feature flag left enabled in production caused an old, deprecated code path to run for every user."},
    {"id": "doc_42", "text": "Auditing feature flags on a monthly schedule and removing stale ones prevented dead code paths from running unexpectedly."},
    {"id": "doc_43", "text": "The staging environment configuration accidentally pointed at the production database, risking a destructive test run."},
    {"id": "doc_44", "text": "Separating environment configs into distinct namespaces with strict access controls prevented staging from ever reaching production data again."},
    {"id": "doc_45", "text": "A rolling update got stuck halfway because the new pod's liveness probe kept failing due to a slow startup sequence."},
    {"id": "doc_46", "text": "Adding a startup probe with a longer grace period let the slow-starting application finish initializing before liveness checks began."},
    {"id": "doc_47", "text": "An autoscaling group launched far more instances than expected because a scaling policy compared the wrong CloudWatch metric."},
    {"id": "doc_48", "text": "Correcting the scaling policy to reference the intended metric brought the instance count back in line with actual demand."},
    {"id": "doc_49", "text": "A shared Terraform state file became locked after a pipeline run was killed mid-apply, blocking every subsequent infrastructure change."},
    {"id": "doc_50", "text": "Manually releasing the stuck Terraform state lock and switching to a remote backend with automatic locking prevented a repeat."},
]
