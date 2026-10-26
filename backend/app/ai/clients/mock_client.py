import json
from typing import Any, Dict, Optional
from app.ai.clients.base import LLMClient


class MockLLM(LLMClient):
    """Deterministic, template-based LLM client for reliable demos and offline tests."""

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        p_lower = prompt.lower()

        # Workout / Meal Plan JSON generation
        if "workout plan" in p_lower or "exercise library" in p_lower:
            plan_data = {
                "title": "3-Day Strength & Conditioning Foundation",
                "days": [
                    {
                        "day_number": 1,
                        "title": "Day 1: Upper Body Push & Core",
                        "exercises": [
                            {"exercise_id": "EX-01", "name": "Barbell Bench Press", "sets": 3, "reps": 10, "rest_sec": 60, "notes": "Keep shoulders retracted"},
                            {"exercise_id": "EX-02", "name": "Dumbbell Shoulder Press", "sets": 3, "reps": 12, "rest_sec": 60, "notes": "Full extension overhead"},
                            {"exercise_id": "EX-03", "name": "Push-Ups", "sets": 3, "reps": 15, "rest_sec": 45, "notes": "Maintain tight core"},
                        ],
                    },
                    {
                        "day_number": 2,
                        "title": "Day 2: Lower Body & Legs",
                        "exercises": [
                            {"exercise_id": "EX-04", "name": "Barbell Back Squat", "sets": 4, "reps": 8, "rest_sec": 90, "notes": "Break parallel safely"},
                            {"exercise_id": "EX-05", "name": "Romanian Deadlift", "sets": 3, "reps": 10, "rest_sec": 60, "notes": "Hinge at the hips"},
                            {"exercise_id": "EX-06", "name": "Walking Lunges", "sets": 3, "reps": 12, "rest_sec": 45, "notes": "Step deliberately"},
                        ],
                    },
                    {
                        "day_number": 3,
                        "title": "Day 3: Pull & Conditioning",
                        "exercises": [
                            {"exercise_id": "EX-07", "name": "Lat Pulldown", "sets": 3, "reps": 10, "rest_sec": 60, "notes": "Pull to upper chest"},
                            {"exercise_id": "EX-08", "name": "Seated Cable Row", "sets": 3, "reps": 12, "rest_sec": 60, "notes": "Squeeze shoulder blades"},
                            {"exercise_id": "EX-09", "name": "Plank", "sets": 3, "reps": 45, "rest_sec": 30, "notes": "Hold neutral spine for 45s"},
                        ],
                    },
                ],
                "notes": "General fitness guidance. Talk to a doctor if you have health problems. Drink 2.5L water daily and warm up 5-10 minutes.",
            }
            return json.dumps(plan_data)

        # Meal Plan JSON generation
        if "meal plan" in p_lower or "local food" in p_lower:
            meal_data = {
                "title": "Sri Lankan High-Protein Balance Plan",
                "days": [
                    {
                        "day_number": 1,
                        "meals": [
                            {"name": "Breakfast", "items": "2 boiled eggs, string hoppers with dhal curry, sambol"},
                            {"name": "Mid-morning", "items": "Fresh banana or papaya slices with black coffee"},
                            {"name": "Lunch", "items": "Red rice (1 cup), grilled fish or chicken (150g), gotukola sambol, dhal"},
                            {"name": "Evening snack", "items": "Roasted chickpeas (kadala) with coconut slices"},
                            {"name": "Dinner", "items": "Steamed vegetables, 2 egg omelette or curd with kithul treacle"},
                        ],
                    }
                ],
                "notes": "Balanced for energy and recovery using everyday Sri Lankan ingredients.",
            }
            return json.dumps(meal_data)

        # Winback Draft
        if "winback" in p_lower or "draft a warm" in p_lower:
            if "sinhala" in p_lower or "si" in p_lower:
                return "ආයුබෝවන්! Iron Peak Fitness එකෙන් අපි ඔබව ටික දිනකින් දැක්කේ නැහැ. ඔබගේ පුහුණුව නැවත ආරම්භ කිරීමට අපි විශේෂ 15% වට්ටමක් සූදානම් කර ඇත්තෙමු. අදම පැමිණෙන්න!"
            elif "tamil" in p_lower or "ta" in p_lower:
                return "வணக்கம்! Iron Peak Fitness இல் உங்களை சில நாட்களாக காணவில்லை. உங்கள் உடற்பயிற்சியை மீண்டும் தொடர 15% விசேட சலுகை உண்டு. இன்றே வாருங்கள்!"
            return "Hey! We missed seeing you at Iron Peak Fitness recently. Consistency is everything, and your team is ready to support you. Come by this week and take 15% off your renewal session!"

        # Ask Gym Analysis
        if "revenue" in p_lower:
            return "Revenue for the current month is Rs 584,000, which is up 14.2% compared to last month (Rs 511,200). Peak collection days remain Saturdays and Mondays."
        if "risk" in p_lower:
            return "There are currently 12 members flagged as at-risk (score 60+). The main reason is dropped visit frequency in the past 14 days. Drafting win-back messages is recommended."
        if "class" in p_lower:
            return "The most popular class is Zumba (Studio A) with a 92% average capacity utilization, followed by HIIT Circuit at 84%."

        # Member Assistant
        if "workout" in p_lower:
            return "Today is Upper Body Push & Core: 3 sets of Barbell Bench Press, Dumbbell Shoulder Press, and Push-Ups. Let's crush it today!"
        if "hours" in p_lower:
            return "Iron Peak Fitness is open Monday to Saturday from 5:30 AM to 10:00 PM, and Sunday from 6:00 AM to 6:00 PM."
        if "dues" in p_lower or "pay" in p_lower:
            return "You currently have no overdue balance. Your membership is active."

        # Default fallback
        return "I am your Ralypto Gym assistant. How can I assist with memberships, workouts, or classes today?"
