# Production Security Checklist & Hardening Roadmap (SECURITY_TODO)

This document provides an honest, rigorous assessment of the security controls implemented in the current build versus the mandatory hardening steps required before handling real financial transactions, live SMS/WhatsApp gateways, or production PII.

---

## 1. What Is Implemented & Secure Today

- **Password & PIN Hashing**: All user passwords and numeric staff PINs are salted and hashed using `bcrypt` via PassLib. Plaintext credentials are never persisted.
- **Tenant Isolation**: Every database table includes `gym_id`. The `get_current_user` dependency binds authenticated operations to the user's tenant ID.
- **Role-Based Access Control (RBAC)**: Strict role hierarchy (`Owner`, `Manager`, `Front desk`, `Trainer`) enforced at FastAPI route endpoints via `@require_role`.
- **Dynamic Check-in QR Codes**: Rotating JWT tokens with a strict **60-second expiration window** and single-use validation prevent replay attacks and screenshot sharing.
- **Human-in-the-Loop Safety**: AI endpoints are prohibited from autonomous external communication or direct modifications to member health records.
- **Input Validation**: Pydantic v2 schemas sanitize all request bodies, query params, and JSON payloads.

---

## 2. Mandatory Items Before Real Money & Production Launch

### A. Authentication & Session Hardening
- [ ] **Refresh Token Rotation**: Implement HttpOnly, Secure, SameSite=Strict cookies for refresh tokens rather than relying solely on bearer JWTs in localStorage.
- [ ] **Multi-Factor Authentication (MFA)**: Require TOTP (e.g. Google Authenticator) for `Owner` and `Manager` accounts.
- [ ] **Account Lockout & Brute-Force Protection**: Limit failed PIN or password attempts to 5 before enforcing a 15-minute lockout.

### B. Payment Gateways & Webhooks
- [ ] **Payment Gateway Integration**: Replace demo payment recording with production SDKs (e.g. PayHere, Stripe, or Commercial Bank of Ceylon IPG).
- [ ] **Webhook Signature Verification**: Verify cryptographic HMAC SHA-256 signatures on all incoming payment gateway notifications to prevent spoofed settlement calls.
- [ ] **PCI-DSS Compliance**: Ensure credit card numbers never touch Ralypto application servers (use hosted fields / checkout elements).

### C. Rate Limiting & Denial of Service Protection
- [ ] **Endpoint Throttling**: Configure Redis-backed `slowapi` or Cloudflare rate limiting:
  - Check-in endpoints: 60 requests/min per IP.
  - Login / PIN verification: 5 requests/min per IP.
  - AI generation endpoints: 10 requests/min per tenant.
- [ ] **Payload Size Limits**: Enforce maximum HTTP request body limits (e.g., 2 MB) to prevent memory exhaustion attacks.

### D. Data Protection & Encryption at Rest
- [ ] **Database Encryption**: When deploying PostgreSQL in production, enforce transparent data encryption (TDE) or disk-level encryption (LUKS / AWS KMS).
- [ ] **PII & Health Record Protection**: Encrypt sensitive PAR-Q health answers and emergency contacts using AES-256 before saving to the database.
- [ ] **Audit Trail Immutability**: Pipe security-sensitive actions (permission changes, refunds, manual member status overrides) to write-once append-only log sinks.

### E. Messaging & Communication Gateways
- [ ] **WhatsApp Business API**: Transition from `https://wa.me/` direct links to official Meta Graph API or Twilio WhatsApp API.
- [ ] **Webhook Signature Verification for SMS Delivery Receipts**: Authenticate incoming delivery status webhooks using shared secret tokens.

### F. Network & Infrastructure
- [ ] **TLS Configuration**: Enforce TLS 1.3 with HSTS enabled on reverse proxies (Nginx / Caddy).
- [ ] **CORS Lockdown**: Restrict `allow_origins` in `main.py` from `["*"]` to explicitly whitelisted gym domain names in production.
- [ ] **Automated Dependency Scanning**: Integrate GitHub Dependabot and Snyk scanning into CI/CD pipelines to catch third-party CVEs.
