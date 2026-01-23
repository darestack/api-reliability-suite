# Security Guide

The API Reliability Suite is designed with a "Secure by Default" mindset, implementing industry-standard protection for authentication, validation, and traffic control.

---

## 🔒 Security Architecture

### Authentication & Authorization

The system uses **JWT (JSON Web Tokens)** for stateless authentication.
- **Provider:** `python-jose`
- **Hashing:** `bcrypt` (via `passlib`)
- **Key Storage:** HMAC-SHA256 with the `SECRET_KEY` environment variable.

#### JWT Workflow
1.  **Login:** Users authenticate at `/login`.
2.  **Token Issuance:** Upon success, a signed JWT is returned with a 30-minute expiration (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
3.  **Verification:** Protected endpoints (e.g., `/protected`, `/debug/summarize-errors`) use the `get_current_user` dependency to validate the token's presence and signature.

---

## 🛡️ Traffic Control & Protection

### Rate Limiting

We use `slowapi` (based on the fixed-window counter algorithm) to protect against brute-force attacks and resource exhaustion.

- **Storage:** Local Memory (default).
- **Strategy:** IP-based tracking via `get_remote_address`.
- **Implementation:** applied via decorators on specific routes (e.g., `@limiter.limit("5/minute")` on `/health`).

### Circuit Breaker

The `pybreaker` implementation protects the API from cascading failures when interacting with external dependencies. If an external service fails repeatedly, the circuit opens, preventing further strain and returning a graceful fallback.

---

## 🧪 Input Validation

### Pydantic Strict Mode

The application uses **Pydantic v2** with `strict=True` enabled in the model configuration. This ensures that:
1.  **Type Safety:** Input types must match exactly (no automatic conversion of strings to ints).
2.  **Schema Enforcement:** Only defined fields are accepted, preventing mass assignment vulnerabilities.

---

## 📋 Security Checklist

### Production Hardening
- [ ] **Change `SECRET_KEY`:** Ensure `SECRET_KEY` is set to a cryptographically strong value in production.
- [ ] **Enforce HTTPS:** Always serve the API behind a TLS-terminating proxy (Nginx, Ingress-Nginx).
- [ ] **Review Log Levels:** Ensure `LOG_LEVEL` is not set to `debug` in production to avoid leaking sensitive metadata.
- [ ] **Scale Rate Limiting:** For distributed deployments, consider migrating `slowapi` storage to Redis.
