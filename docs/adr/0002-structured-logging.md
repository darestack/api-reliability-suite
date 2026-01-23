# 2. Use Structured JSON Logging

Date: 2026-01-22

## Status

Accepted

## Context

In production environments, text-based logs (`INFO: User logged in`) are difficult to query and aggregate.
Debugging a specific request across thousands of log lines is impossible without a unique identifier.

We need a logging solution that:
1.  Outputs machine-readable data (JSON).
2.  Automatically includes context (Trace IDs, Environmental info).
3.  Is easy to parse by log aggregators (Datadog, Splunk, Grafana Loki).

## Decision

We will use **Structlog** as the primary logging library.

*   All logs must be output as **JSON** in production.
*   Every log entry must include a `correlation_id` and `trace_id` if available.
*   Developers must log *events* with *context*, not just sentences.
    *   **Good**: `logger.info("user_login", username="demo", ip="127.0.0.1")`
    *   **Bad**: `logger.info(f"User {username} logged in from {ip}")`

## Consequences

### Positive
*   **Query-ability**: We can search `logs | select where username == "demo"` easily in dashboards.
*   **Context**: Trace IDs are automatically injected, allowing us to stitch logs to traces.
*   **Consistency**: Enforces a standard schema for all log events.

### Negative
*   **Readability**: Raw JSON logs are harder for humans to read in a localized terminal (solved by using `rich` renderer in local dev).
