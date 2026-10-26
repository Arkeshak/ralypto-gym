# AI Features Architecture & Specification - Ralypto Gym

This document details the 6 AI features implemented in the Ralypto Gym Management System, including algorithmic rules, prompt designs, safety guardrails, rate limits, and fallback strategies.

---

## Architecture Overview

```
                      ┌────────────────────────────┐
                      │    AI Feature Service      │
                      │  (Churn, Coach, Assistant) │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │   AI Client Factory        │
                      │  (app.ai.clients.factory)  │
                      └───────┬────────────┬───────┘
                              │            │
       GEMINI_API_KEY is set  │            │  No key or network error
                              ▼            ▼
                     ┌────────────────┐  ┌──────────────────┐
                     │  GeminiClient  │  │     MockLLM      │
                     │ (Gemini 2.5)   │  │ (Deterministic)  │
                     └────────────────┘  └──────────────────┘
```

The system employs a strict **Human-in-the-Loop** model: AI produces drafts, suggestions, and confirmation cards; humans retain full authority before actions or notifications are committed.

---

## Feature Specifications

### AI-1: Churn Risk Scoring & Win-Back Drafter
- **Purpose**: Identify members likely to lapse before their membership expires and draft personalized re-engagement messages.
- **Scoring Engine**:
  - Deterministic formula based on 30-day visit delta, days until renewal, open unpaid dues, and class attendance history.
  - Returns a score from `0` (loyal) to `100` (imminent churn) and an explicit array of human-readable reasons.
- **Message Drafter**:
  - Generates multilingual drafts in English, Sinhala (`ආයුබෝවන් ...`), or Tamil (`வணக்கம் ...`).
  - Saved to `outbox` table with status `draft`.
  - Emits a ready-to-click WhatsApp Web URI (`https://wa.me/{phone}?text=...`).
- **Guardrails**: No messages are dispatched automatically without staff review.

---

### AI-2: AI Workout Coach & Nutrition Planner
- **Purpose**: Draft customized 3-day or 5-day training and nutrition plans based on member goals, experience level, and physical limitations.
- **Safety & Health Form Check**:
  - Automatically queries the member's PAR-Q health questionnaire (`HealthForm`).
  - If `flagged == true` or injuries/medical conditions are noted, the AI plan includes a prominent **Medical Warning Banner** and restricts high-impact exercises.
- **Trainer Approval Gate**:
  - All AI-generated workout and meal plans are saved with `status = "pending_approval"`.
  - Members cannot view plans until a certified trainer taps **Approve** (`status = "approved"`).

---

### AI-3: Member Conversational Assistant
- **Purpose**: In-app conversational assistant for the mobile PWA (`/m/assistant`).
- **Supported Intents**:
  - Class booking queries (*"Book me Zumba tomorrow evening"*).
  - Daily workout guidance (*"What's my workout today?"*).
  - Membership & payment status (*"When is my renewal due?"*).
  - Gym information (*"What are the peak hours today?"*).
- **Confirmation Card Protocol**:
  - Any state-altering request (e.g. reserving a spot in a class) **never** books directly.
  - The assistant responds with `needs_confirmation: true` and an interactive confirmation card containing session details.
  - The booking is created only when the member explicitly submits `confirmed: true`.

---

### AI-4: Intelligent Crowd Forecasting & Best Hours
- **Purpose**: Help members identify quieter gym periods and assist management with trainer staffing.
- **Engine**:
  - Analyzes 90 days of check-in timestamps grouped by hour of day (6 AM – 9 PM) and day of week.
  - Calculates average hourly occupancy normalized against gym floor capacity.
  - Returns recommended off-peak windows (e.g., *"Quieter between 2:00 PM and 4:00 PM"*).

---

### AI-5: "Ask Your Gym" Natural Language Analytics
- **Purpose**: Allow gym owners and managers to query complex business metrics using conversational English or local terminology.
- **Engine**:
  - Queries real-time SQLite database aggregations: monthly net revenue, renewal retention percentage, class capacity utilization, and member acquisition count.
  - Formats responses with clear headline numbers, comparative percentages, and business insights.

---

### AI-6: Automated Weekly Executive Summary
- **Purpose**: Generate a comprehensive Sunday evening report for the gym owner summarizing performance vs. the prior week.
- **Summary Metrics**:
  - Total check-ins vs. previous week (+11.8%).
  - Net revenue collected vs. target.
  - Count of new joins, upcoming renewals, and at-risk members requiring follow-up.
  - Recorded in the `ai_actions` audit log.

---

## LLM Clients & Fallback Policy

1. **`MockLLM`**:
   - Zero-dependency, deterministic client for test environments, offline demos, and CI/CD pipelines.
   - Accurately generates valid JSON schemas for workouts, meal plans, and Sinhala/Tamil win-backs.
2. **`GeminiClient`**:
   - Uses Google's `google-genai` SDK with Gemini 2.5 Flash model.
   - Configured with a 10-second timeout.
   - If `GEMINI_API_KEY` is not present, or if an API quota/rate-limit error occurs, the client **automatically falls back to `MockLLM`** without throwing 500 errors to the user.
