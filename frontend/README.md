# Ralypto Gym frontend

A React and TypeScript frontend scaffold based on the Ralypto Gym Master Agent
Prompt. The staff workspace and mobile member app use seeded, browser-local demo
data so the experience can be explored without a backend.

## Start the frontend

From `frontend/`:

```powershell
npm install
npm run dev
```

Use the Owner, Manager, Front desk, or Trainer selector in the app header to
preview the staff workspace. The member app preview is available from the sidebar.
For a simulated PIN login, open `/login` and enter `1234`.

## Verification

```powershell
npm test
npm run build
```

## Demo boundaries

- Member, payment, check-in, class-booking, and appearance changes live in this
  browser's local storage. They do not reach a server.
- Data, charts, AI insights, receipts, messages, and member information are sample
  content for Iron Peak Fitness.
- AI-generated messages remain drafts. Payment, WhatsApp, SMS, authentication,
  camera QR scanning, offline synchronization, and server APIs are not connected.
- The English, Sinhala, and Tamil selectors demonstrate the language preference;
  application copy has not yet been fully translated.

See [`../docs/PROJECT_STRUCTURE.md`](../docs/PROJECT_STRUCTURE.md) for the original
monorepo plan. This frontend work intentionally leaves the backend scaffold unchanged.
