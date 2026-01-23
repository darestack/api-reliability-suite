# 3. Automated Error Analysis via LLM

Date: 2026-01-22

## Status

Accepted

## Context

When an incident occurs (e.g., 500 Internal Server Error), the "Mean Time To Resolution" (MTTR) is dominated by the initial investigation:
1.  Finding the log.
2.  Reading the stack trace.
3.  Googling the error code.

We want to reduce this time by automating the "Level 1 Support" analysis.

## Decision

We will integrate a **Large Language Model (LLM)** Agent to analyze error logs on-demand.

*   **Trigger**: Authenticated admin hits `/debug/summarize-errors`.
*   **Input**: The raw `app.json` error logs (Sanitized of PII where possible).
*   **Output**: A structured JSON report containing `root_cause`, `severity`, and `remediation_steps`.
*   **Providers**: We support **Groq** (for speed/cost) and **OpenAI** (for quality), selectable via config.

## Consequences

### Positive
*   **Speed**: Instant root cause analysis without manual grep.
*   **Accessibility**: Allows non-expert engineers to understand complex failures (e.g., "Connection Refused at port 4317").
*   **Standardization**: The output is structured, allowing downstream automation (e.g., auto-creating Jira tickets).

### Negative
*   **Cost**: API calls cost money (though Groq/Llama is very cheap).
*   **Privacy**: Logs are sent to a third-party API. Strict data scrubbing is required to ensure no sensitive customer PII (credit cards, passwords) is leaked to the LLM.
