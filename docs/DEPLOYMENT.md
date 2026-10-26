# Client Demo Deployment Guide - Ralypto Gym

This guide provides step-by-step instructions to deploy the Ralypto Gym client demo to **Vercel**, **Netlify**, or **Docker** so you can immediately share a live URL with your client.

---

## ⚡ Option 1: Instant Frontend Deployment to Vercel (Recommended, <2 minutes)

The frontend contains a full standalone interactive client demo with complete client-side data persistence (`localStorage`). Every action (check-in, QR scanning, subscription plan switching, payments, classes, member mobile app, CSV exports, receipts) works 100% out of the box without needing a database connection.

### Method A: Via Vercel CLI
```bash
cd frontend
npm install -g vercel
vercel
```
1. Follow the interactive prompts (accept default settings).
2. Set Framework to **Vite**.
3. Set Build Command to `npm run build` and Output Directory to `dist`.
4. Your live link is immediately generated (e.g. `https://ralypto-gym-demo.vercel.app`).

### Method B: Via Vercel Web Dashboard (GitHub)
1. Push this repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new).
3. Import your GitHub repository.
4. Set **Root Directory** to `frontend`.
5. Keep Build Command as `npm run build` and Output Directory as `dist`.
6. Click **Deploy**.

---

## 🌐 Option 2: Instant Frontend Deployment to Netlify

### Method A: Via Netlify CLI
```bash
cd frontend
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Method B: Drag and Drop `dist` Folder
1. Run build locally:
   ```bash
   cd frontend
   npm run build
   ```
2. Go to [app.netlify.com/drop](https://app.netlify.com/drop).
3. Drag and drop the `frontend/dist` folder onto the browser window.
4. Netlify will deploy it in 5 seconds and give you a public live URL.

---

## 🐳 Option 3: Full-Stack Docker Deployment (Frontend + FastAPI Backend)

If you wish to deploy the full stack with the Python backend API and SQLite database on a VPS (DigitalOcean, AWS, Render, Railway, Hetzner):

```bash
docker compose up -d --build
```
- **Staff & Member Web App**: `http://<your-server-ip>:5173` (or port 80 via Nginx)
- **FastAPI OpenAPI Documentation**: `http://<your-server-ip>:8000/docs`

---

## 🔑 What to Share With Your Client

When sending the link to your client, share this quick-start reference:

### Demo Workspace Details
- **Club Name**: Iron Peak Fitness (Colombo, Sri Lanka)
- **Direct Login**: `/login`

### 1-Click Persona Sign-In
On the login screen, your client can choose any persona with a single click:
1. **Gym Owner**: Full financial overview, revenue analytics, AI retention insights, and subscription tiers.
2. **Club Manager**: Operations, staff shifts, schedule management, and member approvals.
3. **Front Desk Staff**: High-speed check-in, barcode/QR camera scanning simulation, dues collection, and receipt printing.
4. **Personal Trainer**: Client assignment roster, workout plan approval, and 1-on-1 session tracking.
5. **Member Mobile App**: Mobile PWA view (`/m/home`) with interactive rotating QR member pass, workout log, class reservations, and AI fitness assistant.

### Interactive Features to Highlight
- **Subscription Tier Gating**: In **My Plan** (`/app/subscription`), clicking *Switch to Basic*, *Standard*, or *Premium* changes app capabilities in real-time.
- **Instant Check-In**: In **Check-In** (`/app/check-in`), clicking **Scan member QR** simulates instant camera verification of `IPF-1048` (Nimali Perera).
- **One-Click Real Exports**: In **Members**, **Payments**, and **Reports**, clicking **Export** downloads real formatted CSV files (`iron-peak-members.csv`, `iron-peak-payments.csv`, `iron-peak-weekly-report.csv`).
- **Thermal Receipt Printing**: In **Payments**, clicking **Preview receipt** formats and downloads a printable receipt text document.
- **Member AI Assistant**: In Member App (`/m/assistant`), tapping "Book Zumba tomorrow" creates an instant booking with confirmation card.
