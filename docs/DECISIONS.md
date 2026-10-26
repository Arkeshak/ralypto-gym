# Architecture & Design Decisions (ADR) - Ralypto Gym

This document records the architectural, technical, and operational decisions made during the design and construction of the Ralypto Gym Management System.

---

## 1. Database & Persistence Layer

- **Database Engine**: SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
  - *Rationale*: Zero-ops, single-file distribution for on-premise gyms and regional installations. Easily swappable to PostgreSQL via `DATABASE_URL` environment variable without code changes (SQLModel / SQLAlchemy abstraction).
- **Session Model**: SQLModel (`0.0.48`) with synchronous sessions (`sqlmodel.Session`) and thread-pooled operations.
  - *Rationale*: Ensures full compatibility with Pydantic v2 schemas, simplifies nested transactions, and avoids asyncio-in-SQLite event-loop deadlocks.
- **Datetime & Timezone Policy**: All model fields and queries strictly use timezone-aware UTC timestamps (`datetime.now(timezone.utc)` or `datetime.combine(..., tzinfo=timezone.utc)`). Naive datetimes are rejected by SQLModel 0.0.48.
- **Soft-Delete Policy**: Member records are **never hard-deleted**. A `deleted` boolean flag and `leave_reason` field preserve historical attendance, payment receipts, and audit trail integrity.

---

## 2. Multi-Tenancy & Tenant Isolation

- **Tenant Key**: Every business entity (gym, member, payment, check-in, class, workout, lead, AI log) carries a foreign key `gym_id: int` indexed in SQLite.
- **Isolation Enforcement**:
  - `get_current_user` dependency automatically extracts `user.gym_id` from the verified JWT.
  - API routers and service functions require `gym_id` on all CRUD and analytical queries.
  - Cross-tenant queries return HTTP 404 or empty sets, preventing cross-tenant information leakage.

---

## 3. Authentication & Security

- **Password Hashing**: `passlib.context.CryptContext(schemes=["bcrypt"])` with automatic salt generation.
- **Front-Desk PIN Hashing**: Front-desk numeric PINs (default `1234`) are also hashed with bcrypt.
- **JWT Tokens**:
  - Secret: `JWT_SECRET` (configured via environment, minimum 32 chars).
  - Algorithm: `HS256`.
  - Expiry: 7 days (`ACCESS_TOKEN_EXPIRE_MINUTES=10080`) for staff sessions.
- **Dynamic Check-in QR Codes**:
  - Rotating JWT token issued to member mobile app with a **60-second expiration window**.
  - Payload: `{ "sub": member_id, "gym_id": gym_id, "code": member_code, "type": "qr_checkin", "iat": ..., "exp": ... }`.
  - Prevents screenshot sharing, barcode theft, or buddy-punching at the turnstile.

---

## 4. Currency, Locale & Sri Lankan Regionalization

- **Currency**: Sri Lankan Rupee (`LKR`), formatted as `Rs 7,500` or `Rs 12,900.00`. In the backend data model, monetary values are stored in cents (`price_cents`, `joining_fee_cents`, `amount_cents`) to prevent floating-point inaccuracies.
- **Timezone**: Default timezone `Asia/Colombo` (UTC+5:30).
- **Languages Supported**: Trilingual UI ready for English (`en`), Sinhala (`si`), and Tamil (`ta`). AI winback templates are seeded in all 3 languages.
- **Member Identifiers**: Sequential gym-scoped codes, e.g., `IPF-1048` (Iron Peak Fitness).
- **Invoices**: Sequential gym-scoped format `INV-0001`, `INV-0002` with receipt breakdown.

---

## 5. Tier Gating & Feature Flags

- **Tiers**:
  - **Basic**: Up to 150 members, 3 staff accounts, core attendance, payments, check-in, basic reports.
  - **Standard**: Up to 500 members, 10 staff accounts, classes, personal training, workouts, member mobile app, crowd analytics.
  - **Premium**: Unlimited members, unlimited staff, AI workout coach, AI assistant, Ask Gym NLP, weekly summaries, automatic churn win-backs.
- **Enforcement**:
  - Backend: `@require_feature("classes")` and member count checks on creation. Returns HTTP 403 `feature_not_licensed` or `member_limit_reached`.
  - Frontend: Clean "Upgrade to unlock" cards, never silent crashes or raw errors.
  - Dev-only Plan Switcher: Guarded by `VITE_DEV_TOOLS=true`. Dead-code-eliminated from production bundles (`dist/`).

---

## 6. AI Subsystem & Human-in-the-Loop Architecture

- **Pluggable LLM Client Interface**: `app.ai.clients.base.LLMClient` with two implementations:
  1. `MockLLM`: Fully deterministic, zero-network, zero-cost mock that returns high-quality structured JSON and multilingual responses.
  2. `GeminiClient`: Google Gemini 2.5 Flash implementation with timeout, retry, structured prompt templates, and automatic fallback to `MockLLM` if the API key is missing or quota is exhausted.
- **Human-in-the-Loop Guarantee**:
  - AI workout plans are created in `pending_approval` status; trainers must review and approve before members see them.
  - Health form flags (e.g. PAR-Q injuries, cardiovascular history) force a warning banner and trainer sign-off.
  - AI win-back messages are stored as drafts in `outbox`; staff must click send (or open WhatsApp Web) to dispatch.
  - Member assistant booking cards require explicit confirmation (`needs_confirmation: true`) before any database record is created.
