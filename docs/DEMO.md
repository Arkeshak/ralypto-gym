# The 3-Minute Demo Script - Ralypto Gym

This walkthrough demonstrates the end-to-end capabilities of the Ralypto Gym Management System using the seeded **Iron Peak Fitness** workspace.

---

## Prerequisites & Launch

1. **Start Backend**:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --port 8000 --reload
   ```
   API Docs available at: `http://localhost:8000/docs`

2. **Start Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173/` in your browser.

3. **Demo Credentials**:
   - **Workspace**: Iron Peak Fitness (Colombo, Sri Lanka)
   - **Owner Login**: `aru@ironpeak.lk` / `Pass1234!`
   - **Front Desk PIN**: `1234`
   - **Member App Code**: `IPF-1048` (Nimali Perera) / dev OTP: `123456`

---

## 3-Minute Step-by-Step Script

### Minute 1: Front Desk Speed & Check-In Validation
1. Switch to **Front desk** role in the topbar or navigate to `/app/check-in`.
2. Type or scan an active member code: **`IPF-1048`** (Nimali Perera).
   - **Result**: Instant green checkmark banner (<1s response), live gym occupancy counter increments from 18 to 19, sound feedback plays.
3. Type or scan an expired member code: **`IPF-0782`** (Kamal Perera).
   - **Result**: Immediate red warning dialog: *"Membership expired 14 days ago"*. Shows overdue amount and an instant **Renew** button to record payment and restore access in one click.

---

### Minute 2: Retention, AI Churn Signals & Human-in-the-Loop Winback
1. Switch to **Owner** role in the topbar and navigate to `/app/dashboard`.
2. Review the **At-Risk Members** panel highlighting members whose attendance dropped below 50% or whose renewals are pending.
3. Click on **AI Insights** (`/app/ai`) or select a flagged member (e.g., *Kamal Silva*).
4. Review the AI Churn score (e.g., `85/100`) and the computed reasons:
   - *"Visits down 65% in the last 30 days"*
   - *"Renewal due in 5 days with no class bookings"*
5. Tap **Draft win-back message**:
   - The AI generates a warm, personalized win-back message in English, Sinhala, or Tamil.
   - Staff can review and customize the text before dispatching.
6. Tap **Send**:
   - The message is logged to the CRM outbox and generates a one-click WhatsApp direct link (`https://wa.me/...`).

---

### Minute 3: Member Mobile PWA, AI Coach & Natural Language Booking
1. Click **Member App Preview** in the sidebar bottom or open `/m/home`.
2. Notice the dynamic **60-second rotating QR member pass** and the **Crowd Forecast curve** showing quiet hours between 2:00 PM and 4:00 PM.
3. Navigate to `/m/assistant`:
   - Member types or taps suggestion: **"Book Zumba tomorrow"**.
   - The AI Assistant responds with an interactive **Confirmation Card** detailing date, coach, room, and capacity.
   - Tap **Confirm Booking**. The booking is confirmed instantly!
4. Switch back to the Staff app at `/app/classes`:
   - The Zumba session roster immediately shows Nimali Perera registered, proving seamless real-time coordination between member mobile and front desk staff.
5. In `/app/ai`, open **Ask Your Gym**:
   - Type *"How is revenue vs last month?"*
   - Returns clear executive metrics (`Rs 541,300 collected this month, up 9.4%`) alongside category breakdowns and an exportable weekly summary.
