# Ralypto Gym Management System

A multi-tenant, offline-first gym management platform engineered for independent gym owners, front-desk staff, trainers, and fitness members. Tailored for Sri Lankan fitness clubs with native LKR currency formatting, Colombo timezone, and trilingual support (English, Sinhala, Tamil).

---

## System Architecture

- **Backend**: Python 3.10+, FastAPI, SQLModel (SQLAlchemy + Pydantic v2), SQLite (WAL mode) / PostgreSQL compatible, Bcrypt password hashing, JWT authentication with 60-second rotating QR tokens.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS / Vanilla CSS design tokens, Lucide icons, Recharts, VitePWA service worker, Sonner toasts.
- **AI Engine**: Pluggable LLM architecture supporting Google Gemini 2.5 Flash (`GeminiClient`) with automatic graceful fallback to a zero-cost, deterministic `MockLLM`. Human-in-the-loop approval workflows for workouts and CRM messages.
- **Multi-Tenancy**: Strict tenant-isolated data models (`gym_id`) with role-based access control (`Owner`, `Manager`, `Front desk`, `Trainer`) and subscription plan tiers (`Basic`, `Standard`, `Premium`).

---

## Quick Start

### 1. Backend Setup

```powershell
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Seed the database with realistic demo club data (Iron Peak Fitness & City Fit Club)
python -m app.seed

# Start the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation is live at **`http://localhost:8000/docs`**.

### 2. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open **`http://localhost:5173/`** to explore the staff workspace and mobile member app.

### 3. Docker Compose (Alternative)

```powershell
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/docs`

---

## Seed Accounts & Demo Credentials

All demo accounts share the development password: **`Pass1234!`**

| Role | Name | Email | PIN / Code | Notes |
|:---|:---|:---|:---|:---|
| **Gym Owner** | Aru Wijesinghe | `aru@ironpeak.lk` | `1234` | Full access to KPIs, finances, AI, subscriptions |
| **Club Manager** | Dinuka Senanayake | `dinuka@ironpeak.lk` | `1234` | Staff, classes, CRM, operations |
| **Front Desk** | Chathuri Perera | `chathuri@ironpeak.lk` | `1234` | Rapid check-in, member lookup, cash collections |
| **Senior Trainer** | Roshan Silva | `roshan@ironpeak.lk` | `1234` | Workout drafts, PAR-Q reviews, session schedules |
| **Member (PWA)** | Nimali Perera | `nimali@gmail.com` | `IPF-1048` | Rotating QR pass, class bookings, AI assistant (OTP: `123456`) |

---

## Testing & Quality Assurance

### Backend Test Suite (51 Tests)
Covers membership status calculations, sequential payments, 60s rotating QR check-ins, tenant isolation, role/tier gating, and all 6 AI workflows:
```powershell
cd backend
python -m pytest
```
*Output: `51 passed in 18s`*

### Frontend Test Suite (17 Tests)
Covers dashboard loading, member check-ins, member creations, AI assistant confirmations, role-based navigation filtering, plan gating, payments, theme/locale persistence:
```powershell
cd frontend
npm test
```
*Output: `17 passed in 4s`*

### Production Build & Tree-Shaking Audit
```powershell
cd frontend
npm run build
```
*Output: Production bundle ~248 kB JS (~79 kB gzip). Dev tools cleanly removed.*

---

## Subscription Tier Matrix

| Feature | Basic (Rs 5,900/mo) | Standard (Rs 12,900/mo) | Premium (Rs 24,900/mo) |
|:---|:---:|:---:|:---:|
| **Member Limit** | 150 members | 500 members | Unlimited |
| **Staff Accounts** | 3 accounts | 10 accounts | Unlimited |
| **Core Check-in & Payments** | Yes | Yes | Yes |
| **Classes & Booking Timetable** | No | Yes | Yes |
| **Member Mobile App (`/m/*`)** | No | Yes | Yes |
| **Workouts & Exercise Library** | No | Yes | Yes |
| **Crowd Forecast Curve** | No | Yes | Yes |
| **AI Workout Coach & Meal Plans** | No | No | Yes |
| **AI Member Assistant (`/m/assistant`)** | No | No | Yes |
| **AI Churn Scoring & Win-backs** | No | No | Yes |
| **"Ask Your Gym" Natural Language** | No | No | Yes |
| **Weekly Executive Summary** | No | No | Yes |

*Note: Dev-only plan switcher is active only when `VITE_DEV_TOOLS=true` and is completely stripped from production builds.*

---

## Documentation Index

- [Architecture Decisions (ADR)](docs/DECISIONS.md) - Database, session model, timezone constraints, and security policies.
- [3-Minute Demo Script](docs/DEMO.md) - Step-by-step walkthrough of the 5 core demo flows.
- [Frontend Status & Audit](docs/FRONTEND_STATUS.md) - Bundle sizes, responsive checks (1280/1024/768/390px), translations, and print styles.
- [AI Subsystem Specification](docs/AI_FEATURES.md) - Algorithmic rules, prompts, guardrails, and Gemini/MockLLM fallbacks.
- [Security Hardening Roadmap](docs/SECURITY_TODO.md) - Honest checklist of controls required prior to live financial operations.
- [OpenAPI Specification](docs/openapi.json) - Full REST API contract (FastAPI v1 schema).
