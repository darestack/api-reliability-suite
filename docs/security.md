# Security Guide

The API Reliability Suite is designed with a "Secure by Default" mindset, implementing industry-standard protection for authentication, validation, and traffic control.

---

## 🔒 Security Architecture

### Authentication & Authorization

The system uses **JWT access tokens plus persisted refresh sessions** for authentication.
- **Provider:** `python-jose`
- **Hashing:** `bcrypt`
- **Key Storage:** HMAC-SHA256 with `SECRET_KEY` loaded from env vars or secret files.
- **Persistence:** User records are loaded from the configured relational database via SQLAlchemy.
- **Session Storage:** Refresh-token rotation and access-token revocation are stored in the relational database.

#### JWT Workflow
1.  **Login:** Users authenticate at `/login`.
2.  **Token Issuance:** Upon success, the API returns an access token plus a refresh token.
3.  **Rotation:** `/token/refresh` rotates the refresh token and issues a fresh token pair.
4.  **Revocation:** `/logout` revokes the current access token and can also revoke the presented refresh token.
5.  **Authorization:** Sensitive routes such as `/debug/summarize-errors` require the `admin` role.

---

## 🛡️ Traffic Control & Protection

### Rate Limiting

We use `slowapi` (based on the fixed-window counter algorithm) to protect against brute-force attacks and resource exhaustion.

- **Storage:** Configurable via `RATE_LIMIT_STORAGE_URI` (Redis recommended for shared deployments).
- **Strategy:** IP-based tracking via `get_remote_address`.
- **Implementation:** applied via decorators on specific routes (e.g., `@limiter.limit("5/minute")` on `/health`).

### Circuit Breaker

The `pybreaker` implementation protects the API from cascading failures when interacting with external dependencies. If an external service fails repeatedly, the circuit opens, preventing further strain and returning a graceful fallback. When `CIRCUIT_BREAKER_CACHE_URL` is configured, the fallback can serve the latest cached success payload from Redis.

### Reverse Proxy and Host Validation

The API can enforce deployment-facing controls through middleware:

- **Trusted hosts:** `TRUSTED_HOSTS` enables `TrustedHostMiddleware`.
- **CORS:** `CORS_ALLOW_ORIGINS` enables `CORSMiddleware`.
- **HTTPS redirects:** `HTTPS_REDIRECT_ENABLED=true` enables `HTTPSRedirectMiddleware`.

These controls are intended for deployments behind a TLS-terminating reverse proxy or ingress.

## 🔍 AI Log-Triage Safeguards

Before the app sends error logs to an LLM provider, it:

- filters to error-level lines only
- redacts common secret-bearing keys such as `password`, `token`, and `authorization`
- redacts common PII or credential patterns such as email addresses, bearer tokens, JWTs, and IPv4 addresses

This keeps the summarization path narrower than raw log forwarding.

---

## 🧪 Input Validation

### Pydantic Strict Mode

The application uses **Pydantic v2** with `strict=True` enabled in the model configuration. This ensures that:
1.  **Type Safety:** Input types must match exactly (no automatic conversion of strings to ints).
2.  **Schema Enforcement:** Only defined fields are accepted, preventing mass assignment vulnerabilities.

---

## 📋 Production Readiness Standard

### Security Hardening Audit
- [ ] **Change `SECRET_KEY`:** Ensure `SECRET_KEY` is set to a cryptographically strong value in production.
- [ ] **Use Postgres (or equivalent):** Point `DATABASE_URL` to a server-grade relational database in shared environments.
- [ ] **Use Secret Files:** Mount secrets under `/run/secrets` or set `SETTINGS_SECRETS_DIR`.
- [ ] **Enforce HTTPS:** Always serve the API behind a TLS-terminating proxy (Nginx, Ingress-Nginx).
- [ ] **Review Log Levels:** Ensure `LOG_LEVEL` is not set to `debug` in production to avoid leaking sensitive metadata.
- [ ] **Scale Rate Limiting:** Use Redis-backed storage via `RATE_LIMIT_STORAGE_URI` for distributed deployments.
- [ ] **Protect Fallback Cache:** Use Redis-backed fallback storage via `CIRCUIT_BREAKER_CACHE_URL` for degraded response continuity.

## ✅ Production Hardening Checklist

- Set `ENVIRONMENT=production` and verify the app fails fast with default secrets.
- Set `DATABASE_URL` to a shared relational database before shared deployment.
- Provide `SECRET_KEY` via a secrets file or trusted secret manager.
- Configure `RATE_LIMIT_STORAGE_URI` with Redis for shared deployments.
- Configure `CIRCUIT_BREAKER_CACHE_URL` with Redis for cache-backed fallback responses.
- Keep `RATE_LIMIT_IN_MEMORY_FALLBACK_ENABLED=false` in production.
- Run behind TLS and restrict access to `/metrics` if exposed.
- Configure `TRUSTED_HOSTS` and `CORS_ALLOW_ORIGINS` explicitly in shared environments.
- Keep the admin-only AI triage path behind role-based access.
