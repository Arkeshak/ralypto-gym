from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from sqlmodel import Session, select
from app.models.checkin import CheckIn
from app.services.checkin_service import get_live_attendance


def get_crowd_forecast(session: Session, gym_id: str) -> Dict[str, Any]:
    live_data = get_live_attendance(session, gym_id)
    live_count = live_data["live_count"]

    # Calculate hourly average distribution based on historical check-ins
    # Hours 6 AM to 10 PM (6 to 22)
    # Peak hours: 6-8 AM, 5-8 PM (17-20)
    history = session.exec(
        select(CheckIn).where(CheckIn.gym_id == gym_id, CheckIn.result == "ok")
    ).all()

    hour_counts = {h: 0 for h in range(6, 23)}
    total_days = max(1, len(set(c.checked_in_at.date() for c in history)))

    for c in history:
        h = c.checked_in_at.hour
        if h in hour_counts:
            hour_counts[h] += 1

    # Normalize to 0-100 index
    hourly_bars = []
    max_hour_avg = max(1, max(hour_counts.values()) / total_days)

    for h in range(6, 23):
        avg = hour_counts[h] / total_days
        # Smooth with standard gym baseline curve if data is small
        if total_days < 7:
            if h in [6, 7, 17, 18, 19]:
                busy_index = 85
            elif h in [8, 9, 16, 20]:
                busy_index = 55
            elif h in [12, 13, 14, 15]:
                busy_index = 22
            else:
                busy_index = 35
        else:
            busy_index = min(100, int((avg / max_hour_avg) * 100))

        label = "Quiet" if busy_index < 40 else ("Normal" if busy_index < 70 else "Busy")
        ampm = "AM" if h < 12 else "PM"
        display_h = h if h <= 12 else h - 12
        if display_h == 0:
            display_h = 12

        hourly_bars.append({
            "hour": h,
            "display": f"{display_h} {ampm}",
            "level": busy_index,
            "status": label,
        })

    current_hour = datetime.now(timezone.utc).hour
    current_level = next((b["level"] for b in hourly_bars if b["hour"] == current_hour), 40)
    current_status = "Quiet" if current_level < 40 else ("Normal" if current_level < 70 else "Busy")

    return {
        "live_count": live_count,
        "current_status": current_status,
        "current_level": current_level,
        "best_time_to_go": "Today 1:00 PM – 4:00 PM (Quiet, low wait times for racks)",
        "staffing_advice": "Peak occupancy expected between 5:30 PM – 8:00 PM. Recommend floor trainer on duty.",
        "hourly_distribution": hourly_bars,
    }
