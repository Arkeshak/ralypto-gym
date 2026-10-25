# Ralypto Gym Project Structure

This is the initial, code-free scaffold for the Ralypto Gym management system. It
follows the **Ralypto Gym Master Agent Prompt (2-Day Build)**. Directories are
intentionally empty; `.gitkeep` files only preserve them in version control.

## Decisions captured from the prompt

- Monorepo with `frontend/`, `backend/`, and `docs/`.
- Frontend: React, TypeScript, and Vite; staff and mobile-first member areas share
  one progressive web app.
- Backend: FastAPI with SQLModel, Pydantic, and SQLite by default, with PostgreSQL
  supported through configuration.
- Backend owns authentication, role/tenant checks, plan entitlements, and business
  rules. AI features live inside the backend and call permission-checked services.
- English, Sinhala, and Tamil are planned application locales.
- This scaffold does not implement features, add dependencies, or create runnable
  application/configuration files.

## Directory map

```text
.
|-- docs/
|   |-- api/
|   |-- architecture/
|   |-- demo/
|   |-- operations/
|   |-- product/
|   |-- security/
|   `-- testing/
|-- frontend/
|   |-- e2e/
|   |   |-- auth/
|   |   |-- check-in/
|   |   |-- memberships/
|   |   `-- member-booking/
|   |-- public/
|   |   `-- icons/
|   `-- src/
|       |-- app/
|       |   |-- providers/
|       |   `-- routing/
|       |-- components/
|       |   |-- feedback/
|       |   |-- forms/
|       |   |-- layout/
|       |   `-- ui/
|       |-- features/
|       |   |-- ai-center/
|       |   |-- auth/
|       |   |-- check-in/
|       |   |-- classes/
|       |   |-- crm/
|       |   |-- dashboard/
|       |   |-- member-app/
|       |   |   |-- assistant/
|       |   |   |-- classes/
|       |   |   |-- home/
|       |   |   |-- profile/
|       |   |   |-- progress/
|       |   |   `-- workouts/
|       |   |-- members/
|       |   |-- membership-plans/
|       |   |-- messages/
|       |   |-- payments/
|       |   |-- progress/
|       |   |-- reports/
|       |   |-- settings/
|       |   |-- staff/
|       |   |-- subscription/
|       |   |-- trainers/
|       |   `-- workouts/
|       |-- lib/
|       |   |-- api/
|       |   |-- auth/
|       |   |-- formatting/
|       |   |-- i18n/
|       |   |-- offline/
|       |   |-- permissions/
|       |   `-- qr/
|       |-- locales/
|       |   |-- en/
|       |   |-- si/
|       |   `-- ta/
|       |-- styles/
|       `-- test/
|           |-- fixtures/
|           `-- mocks/
|-- backend/
|   |-- alembic/
|   |   `-- versions/
|   |-- app/
|   |   |-- ai/
|   |   |   |-- clients/
|   |   |   |-- features/
|   |   |   |-- schemas/
|   |   |   `-- tools/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |       `-- routes/
|   |   |-- core/
|   |   |-- db/
|   |   |-- jobs/
|   |   |-- messaging/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- security/
|   |   |-- seed/
|   |   `-- services/
|   `-- tests/
|       |-- api/
|       |-- factories/
|       |-- integration/
|       `-- unit/
`-- scripts/
```

## Planned ownership

- `frontend/src/features/`: user-facing product areas; `member-app/` is the
  mobile-first member experience, while the other feature folders serve staff.
- `frontend/src/components/` and `frontend/src/lib/`: shared presentation and
  cross-feature utilities, respectively.
- `frontend/src/locales/`: English (`en`), Sinhala (`si`), and Tamil (`ta`)
  translation resources.
- `backend/app/api/v1/routes/`: versioned HTTP endpoints. Route handlers should
  delegate to services rather than contain business rules.
- `backend/app/models/`, `schemas/`, and `services/`: persistence models, API
  contracts, and business operations.
- `backend/app/security/`: authentication, role checks, and tenant-scope
  enforcement.
- `backend/app/ai/`: LLM clients, AI feature workflows, validated output schemas,
  and permission-scoped tools. AI actions must use backend services; they must not
  write to the database directly.
- `backend/app/jobs/` and `backend/app/messaging/`: scheduled work and outbound
  message-provider integrations.
- `backend/tests/` and `frontend/e2e/`: backend unit/API/integration coverage and
  end-to-end user flows.
- `docs/`: API, architecture, demo, operations, product, security, and testing
  documentation.
- `scripts/`: future development and maintenance utilities.

## Scaffold boundary

No source code, dependency manifests, environment files, Docker configuration,
database migrations, or runnable scripts have been added. Those belong to the
implementation stage after this structure is reviewed.
