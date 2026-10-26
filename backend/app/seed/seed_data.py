from datetime import date, datetime, timedelta, timezone
import json
import random
from sqlmodel import Session, select
from app.db.session import engine, init_db
from app.models.ai import ChurnScore
from app.models.base import utc_now
from app.models.checkin import CheckIn
from app.models.class_model import Booking, Class, ClassSession
from app.models.crm import Lead, Message
from app.models.gym import Gym, GymSettings
from app.models.member import HealthForm, Member
from app.models.payment import Due, Payment
from app.models.plan import Freeze, Membership, MembershipPlan
from app.models.user import User
from app.models.workout import Exercise, WorkoutPlan
from app.security.passwords import hash_password, hash_pin
from app.services.membership_service import compute_membership_status


FIRST_NAMES = [
    "Nimali", "Kavindu", "Tharushi", "Ravindu", "Ayesha", "Isuru", "Sachini", "Dilan",
    "Minoli", "Ashen", "Dinithi", "Chathura", "Sanduni", "Lahiru", "Anuki", "Roshan",
    "Chamari", "Gayan", "Niroshan", "Kaveesha", "Malik", "Shalani", "Buddhika", "Dilshan",
    "Hasini", "Nuwan", "Ruvini", "Sameera", "Nadeesha", "Sanath", "Pravin", "Fathima",
    "Rukshan", "Dulani", "Mahesh", "Shenali", "Supun", "Nethmi", "Vishwa", "Anjalee"
]

LAST_NAMES = [
    "Perera", "Fernando", "Jayasinghe", "de Silva", "Wickramasinghe", "Bandara",
    "Gunawardena", "Samaraweera", "Rodrigo", "Jayawardene", "Alwis", "Herath",
    "Fonseka", "Rajapaksha", "Mendis", "Dissanayake", "Senanayake", "Liyanage",
    "Karunaratne", "Wijesinghe", "Abeysekara", "Cooray", "Nanayakkara", "Kulasekara"
]


def seed_database():
    init_db()
    with Session(engine) as session:
        # Check if already seeded
        existing_gym = session.exec(select(Gym).where(Gym.code == "IPF")).first()
        if existing_gym:
            print("Database already seeded with Iron Peak Fitness. Skipping re-seed.")
            return

        print("Seeding Iron Peak Fitness...")

        # 1. Demo Gym: Iron Peak Fitness
        gym = Gym(
            name="Iron Peak Fitness",
            code="IPF",
            phone="+94 11 258 9000",
            address="42 Galle Road, Colombo 03, Sri Lanka",
            plan="Premium",
            plan_status="active",
            plan_renews_at=utc_now() + timedelta(days=90),
            timezone="Asia/Colombo",
            currency="LKR",
        )
        session.add(gym)
        session.commit()
        session.refresh(gym)

        # Gym Settings
        settings = GymSettings(
            gym_id=gym.id,
            grace_days=7,
            late_cancel_hours=2,
            auto_checkout_hours=3,
            receipt_header="Iron Peak Fitness - Colombo Flagship",
            receipt_footer="Train hard, stay consistent! Tel: +94 11 258 9000",
        )
        session.add(settings)

        # 2. Staff Logins
        pwd_hash = hash_password("Pass1234!")
        pin_hash = hash_pin("1234")

        staff_data = [
            ("Roshan Jayasinghe", "owner@ironpeak.lk", "+94 77 100 0001", "owner", None),
            ("Nirosha Mendis", "manager@ironpeak.lk", "+94 77 100 0002", "manager", None),
            ("Kasun Frontdesk", "frontdesk@ironpeak.lk", "+94 77 100 0003", "front_desk", pin_hash),
            ("Kasun Silva", "trainer.kasun@ironpeak.lk", "+94 77 100 0004", "trainer", None),
            ("Maya de Alwis", "trainer.maya@ironpeak.lk", "+94 77 100 0005", "trainer", None),
        ]

        trainer_users = []
        for name, email, phone, role, p_hash in staff_data:
            user = User(
                gym_id=gym.id,
                name=name,
                email=email,
                phone=phone,
                role=role,
                password_hash=pwd_hash,
                pin_hash=p_hash,
                active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            if role == "trainer":
                trainer_users.append(user)

        # 3. Membership Plans
        plans_data = [
            ("Day Pass", 1, 80000, 0, 0),
            ("Monthly", 30, 500000, 200000, 7),
            ("Student", 30, 400000, 100000, 7),
            ("Couple Monthly", 30, 850000, 300000, 7),
            ("Quarterly", 90, 1350000, 0, 14),
            ("Yearly", 365, 4800000, 0, 30),
        ]
        created_plans = []
        for name, dur, price, join_fee, freeze_days in plans_data:
            p = MembershipPlan(
                gym_id=gym.id,
                name=name,
                duration_days=dur,
                price_cents=price,
                joining_fee_cents=join_fee,
                max_freeze_days=freeze_days,
                active=True,
            )
            session.add(p)
            session.commit()
            session.refresh(p)
            created_plans.append(p)

        monthly_plan = created_plans[1]
        quarterly_plan = created_plans[4]
        yearly_plan = created_plans[5]

        # 4. Exercise Library (40 Exercises)
        exercises_specs = [
            ("Barbell Bench Press", "Chest", "barbell", "intermediate", "[]"),
            ("Incline Dumbbell Press", "Chest", "dumbbell", "beginner", "[]"),
            ("Cable Chest Fly", "Chest", "cable", "beginner", "[]"),
            ("Push-Ups", "Chest", "bodyweight", "beginner", "[]"),
            ("Dips", "Chest", "bodyweight", "intermediate", '["shoulder_pain"]'),
            ("Barbell Back Squat", "Legs", "barbell", "intermediate", '["knee_pain", "lower_back"]'),
            ("Romanian Deadlift", "Hamstrings", "barbell", "intermediate", '["lower_back"]'),
            ("Leg Press", "Legs", "machine", "beginner", "[]"),
            ("Walking Dumbbell Lunges", "Legs", "dumbbell", "beginner", '["knee_pain"]'),
            ("Leg Extension", "Quadriceps", "machine", "beginner", '["knee_pain"]'),
            ("Lying Hamstring Curl", "Hamstrings", "machine", "beginner", "[]"),
            ("Standing Calf Raise", "Calves", "machine", "beginner", "[]"),
            ("Conventional Deadlift", "Back", "barbell", "advanced", '["lower_back"]'),
            ("Lat Pulldown", "Back", "cable", "beginner", "[]"),
            ("Seated Cable Row", "Back", "cable", "beginner", "[]"),
            ("Single Arm Dumbbell Row", "Back", "dumbbell", "beginner", "[]"),
            ("Pull-Ups", "Back", "bodyweight", "intermediate", "[]"),
            ("T-Bar Row", "Back", "barbell", "intermediate", '["lower_back"]'),
            ("Standing Barbell Overhead Press", "Shoulders", "barbell", "intermediate", '["shoulder_pain"]'),
            ("Seated Dumbbell Shoulder Press", "Shoulders", "dumbbell", "beginner", '["shoulder_pain"]'),
            ("Dumbbell Lateral Raise", "Shoulders", "dumbbell", "beginner", "[]"),
            ("Cable Face Pulls", "Shoulders", "cable", "beginner", "[]"),
            ("Reverse Pec Deck Fly", "Shoulders", "machine", "beginner", "[]"),
            ("Barbell Bicep Curl", "Biceps", "barbell", "beginner", "[]"),
            ("Incline Dumbbell Curl", "Biceps", "dumbbell", "beginner", "[]"),
            ("Cable Hammer Curl", "Biceps", "cable", "beginner", "[]"),
            ("EZ Bar Preacher Curl", "Biceps", "barbell", "intermediate", "[]"),
            ("Tricep Rope Pushdown", "Triceps", "cable", "beginner", "[]"),
            ("Skull Crushers", "Triceps", "barbell", "intermediate", '["elbow_pain"]'),
            ("Overhead Dumbbell Tricep Extension", "Triceps", "dumbbell", "beginner", "[]"),
            ("Close Grip Bench Press", "Triceps", "barbell", "intermediate", "[]"),
            ("Plank", "Core", "bodyweight", "beginner", "[]"),
            ("Hanging Leg Raise", "Core", "bodyweight", "intermediate", "[]"),
            ("Cable Woodchoppers", "Core", "cable", "beginner", "[]"),
            ("Ab Wheel Rollout", "Core", "bodyweight", "advanced", '["lower_back"]'),
            ("Russian Twists", "Core", "bodyweight", "beginner", "[]"),
            ("Rowing Ergometer 500m", "Cardio", "cardio", "beginner", "[]"),
            ("Assault AirBike Sprints", "Cardio", "cardio", "intermediate", "[]"),
            ("Kettlebell Swings", "Full Body", "kettlebell", "intermediate", '["lower_back"]'),
            ("Burpees", "Full Body", "bodyweight", "intermediate", "[]"),
        ]

        created_exercises = []
        for name, muscle, eq, lvl, contra in exercises_specs:
            ex = Exercise(
                gym_id=gym.id,
                name=name,
                muscle_group=muscle,
                equipment=eq,
                level=lvl,
                how_to="Execute with controlled form and steady breathing.",
                contraindications_json=contra,
            )
            session.add(ex)
            session.commit()
            session.refresh(ex)
            created_exercises.append(ex)

        # 5. Classes & Sessions
        classes_data = [
            ("HIIT Circuit", "High-intensity metabolic conditioning", trainer_users[0].id, "Studio A", 18, 45),
            ("Morning Yoga", "Mobility, balance, and breathwork", trainer_users[1].id, "Studio B", 15, 60),
            ("Strength Lab", "Hypertrophy and barbell fundamentals", trainer_users[0].id, "Main floor", 16, 60),
            ("Zumba", "Latin dance cardio and rhythm workout", trainer_users[1].id, "Studio A", 22, 50),
            ("Boxing Basics", "Pad work, footwork, and core", trainer_users[0].id, "Studio C", 14, 45),
            ("Pilates Core", "Postural alignment and deep core", trainer_users[1].id, "Studio B", 16, 50),
            ("Power Spin", "High-cadence interval cycling", trainer_users[0].id, "Spin Room", 20, 45),
            ("Cross Conditioning", "Functional weights and agility", trainer_users[0].id, "Outdoor Turf", 15, 60),
        ]

        created_classes = []
        for cname, cdesc, tid, rm, cap, dur in classes_data:
            c = Class(
                gym_id=gym.id,
                name=cname,
                description=cdesc,
                trainer_id=tid,
                room=rm,
                capacity=cap,
                duration_min=dur,
                active=True,
            )
            session.add(c)
            session.commit()
            session.refresh(c)
            created_classes.append(c)

        # Weekly Class Sessions
        now = utc_now()
        created_sessions = []
        for i, c in enumerate(created_classes):
            for day_offset in range(7):
                sess_time = now + timedelta(days=day_offset, hours=i * 2 - 4)
                cs = ClassSession(
                    gym_id=gym.id,
                    class_id=c.id,
                    starts_at=sess_time,
                    capacity=c.capacity,
                    status="scheduled",
                )
                session.add(cs)
                session.commit()
                session.refresh(cs)
                created_sessions.append(cs)

        # 6. Seed 120 Members with mixed statuses and checkin history
        print("Generating 120 realistic Sri Lankan members...")
        today = date.today()

        members = []
        # Target mix: 60% active (72), 10% expiring (12), 8% grace (10), 15% expired (18), 4% frozen (5), 3% stopped (3)
        categories = (
            ["active"] * 72
            + ["expiring"] * 12
            + ["grace"] * 10
            + ["expired"] * 18
            + ["frozen"] * 5
            + ["stopped"] * 3
        )
        random.shuffle(categories)

        for i in range(120):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            code = f"IPF-{1001 + i}"
            phone = f"+94 7{random.choice([0, 1, 2, 5, 6, 7, 8])} {random.randint(100, 999)} {random.randint(1000, 9999)}"
            email = f"{fn.lower()}.{ln.lower()}{random.randint(1, 99)}@gmail.com"
            goal = random.choice(["Build muscle", "Fat loss", "Endurance & stamina", "Strength foundation", "Mobility"])
            joined_dt = utc_now() - timedelta(days=random.randint(30, 450))

            m = Member(
                gym_id=gym.id,
                member_code=code,
                name=f"{fn} {ln}",
                phone=phone,
                email=email,
                gender="Male" if i % 2 == 0 else "Female",
                goal=goal,
                joined_at=joined_dt,
                trainer_id=trainer_users[i % 2].id,
            )
            session.add(m)
            session.commit()
            session.refresh(m)
            members.append((m, categories[i]))

        # Memberships, Freezes, and Payments for each member
        for idx, (m, cat) in enumerate(members):
            plan = random.choice(created_plans[1:])  # Monthly, Student, Quarterly, etc.

            if cat == "active":
                start = today - timedelta(days=random.randint(5, 20))
                end = start + timedelta(days=plan.duration_days)
                ms_status = "active"
            elif cat == "expiring":
                # ends within 7 days
                end = today + timedelta(days=random.randint(1, 6))
                start = end - timedelta(days=plan.duration_days)
                ms_status = "expiring"
            elif cat == "grace":
                # ended within 7 days
                end = today - timedelta(days=random.randint(1, 6))
                start = end - timedelta(days=plan.duration_days)
                ms_status = "grace"
            elif cat == "expired":
                end = today - timedelta(days=random.randint(15, 60))
                start = end - timedelta(days=plan.duration_days)
                ms_status = "expired"
            elif cat == "frozen":
                start = today - timedelta(days=15)
                end = today + timedelta(days=20)
                ms_status = "frozen"
            else:  # stopped
                start = today - timedelta(days=90)
                end = today - timedelta(days=60)
                ms_status = "stopped"
                m.status_override = "stopped"
                m.leave_reason = "Relocated"
                session.add(m)

            ms = Membership(
                gym_id=gym.id,
                member_id=m.id,
                plan_id=plan.id,
                start_date=start,
                end_date=end,
                status=ms_status,
                frozen_days_used=7 if cat == "frozen" else 0,
            )
            session.add(ms)
            session.commit()
            session.refresh(ms)

            # Record payments
            pmt = Payment(
                gym_id=gym.id,
                member_id=m.id,
                membership_id=ms.id,
                amount_cents=plan.price_cents,
                method=random.choice(["cash", "card", "bank"]),
                invoice_no=f"INV-{(idx + 1):04d}",
                paid_at=datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc),
            )
            session.add(pmt)

            # Open dues for 8 specific members
            if idx in [7, 14, 23, 35, 48, 62, 81, 99]:
                due = Due(
                    gym_id=gym.id,
                    member_id=m.id,
                    amount_cents=plan.price_cents,
                    due_date=today - timedelta(days=random.randint(3, 15)),
                    status="open",
                    reason=f"{plan.name} Renewal Fee",
                )
                session.add(due)

        # 7. Check-in History (90 Days, Realistic Peaks 6-8 AM & 5-8 PM)
        print("Seeding 90 days of check-in patterns...")
        for day_ago in range(90):
            day_dt = today - timedelta(days=day_ago)
            # Weekend vs weekday
            is_weekend = day_dt.weekday() in [5, 6]
            daily_visits = random.randint(30, 50) if is_weekend else random.randint(55, 85)

            # Pick active members
            active_pool = [m for m, c in members if c in ["active", "expiring", "grace"]]
            sample_attendees = random.sample(active_pool, min(daily_visits, len(active_pool)))

            for m in sample_attendees:
                # 60% peak morning (6-8 AM) or peak evening (17-20 PM)
                r = random.random()
                if r < 0.35:
                    hr = random.choice([6, 7, 8])
                elif r < 0.75:
                    hr = random.choice([17, 18, 19, 20])
                else:
                    hr = random.choice([9, 10, 11, 12, 13, 14, 15, 16])

                minute = random.randint(0, 59)
                checkin_time = datetime.combine(day_dt, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=hr, minutes=minute)

                ci = CheckIn(
                    gym_id=gym.id,
                    member_id=m.id,
                    checked_in_at=checkin_time,
                    checked_out_at=checkin_time + timedelta(minutes=random.randint(45, 90)),
                    method=random.choice(["qr", "phone", "manual"]),
                    result="ok",
                )
                session.add(ci)

        # 8. Compute Churn Scores for All Members
        print("Computing churn risk scores...")
        from app.ai.features.churn import compute_all_churn_scores
        compute_all_churn_scores(session, gym.id)

        # 9. 3 Dedicated Member User Logins (code 123456)
        # Nimali Perera, Kavindu Fernando, Tharushi Jayasinghe
        for i in range(3):
            mem, _ = members[i]
            user = User(
                gym_id=gym.id,
                name=mem.name,
                phone=mem.phone,
                email=mem.email,
                role="member",
                active=True,
                linked_member_id=mem.id,
            )
            session.add(user)

        # 10. Workout Plans: 1 Approved + 1 Pending AI
        approved_plan = WorkoutPlan(
            gym_id=gym.id,
            member_id=members[0][0].id,
            created_by="AI Coach",
            source="ai",
            status="approved",
            title="3-Day Strength Foundation",
            days_json=json.dumps([
                {
                    "day_number": 1,
                    "title": "Push Power",
                    "exercises": [
                        {"exercise_id": created_exercises[0].id, "name": "Barbell Bench Press", "sets": 3, "reps": 10},
                        {"exercise_id": created_exercises[1].id, "name": "Incline Dumbbell Press", "sets": 3, "reps": 12},
                    ],
                }
            ]),
            approved_by=trainer_users[0].name,
            approved_at=utc_now() - timedelta(days=2),
        )
        session.add(approved_plan)

        pending_plan = WorkoutPlan(
            gym_id=gym.id,
            member_id=members[1][0].id,
            created_by="AI Coach",
            source="ai",
            status="pending_approval",
            title="Hypertrophy Circuit - Pending Review",
            days_json=json.dumps([
                {
                    "day_number": 1,
                    "title": "Lower Body Focus",
                    "exercises": [
                        {"exercise_id": created_exercises[5].id, "name": "Barbell Back Squat", "sets": 4, "reps": 8},
                        {"exercise_id": created_exercises[6].id, "name": "Romanian Deadlift", "sets": 3, "reps": 10},
                    ],
                }
            ]),
            notes="General fitness guidance. Trainer review pending.",
        )
        session.add(pending_plan)

        # 11. Leads (30 leads across New, Trial, Joined, Lost)
        lead_sources = ["walk_in", "instagram", "referral", "web"]
        lead_statuses = ["new"] * 12 + ["trial"] * 8 + ["joined"] * 6 + ["lost"] * 4
        for i in range(30):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            lead = Lead(
                gym_id=gym.id,
                name=f"{fn} {ln}",
                phone=f"+94 77 {random.randint(100, 999)} {random.randint(1000, 9999)}",
                email=f"{fn.lower()}.lead{i}@mail.lk",
                source=random.choice(lead_sources),
                status=lead_statuses[i],
                score=random.randint(35, 95),
                notes="Interested in evening classes and weights." if i % 2 == 0 else "Looking for personal training.",
            )
            session.add(lead)

        # 12. Tiny Second Demo Gym for Tenant Isolation Testing
        tenant_gym = Gym(
            name="City Fit Club",
            code="CFC",
            phone="+94 11 200 1111",
            address="Kandy Road, Kiribathgoda",
            plan="Basic",
            plan_status="active",
        )
        session.add(tenant_gym)
        session.commit()
        session.refresh(tenant_gym)

        # 5 members in tiny gym
        for k in range(5):
            tm = Member(
                gym_id=tenant_gym.id,
                member_code=f"CFC-10{k+1}",
                name=f"City Member {k+1}",
                phone=f"+94 71 999 000{k}",
                email=f"citymember{k+1}@mail.lk",
                goal="General health",
            )
            session.add(tm)

        tenant_user = User(
            gym_id=tenant_gym.id,
            name="City Manager",
            email="manager@cityfit.lk",
            role="manager",
            password_hash=pwd_hash,
            active=True,
        )
        session.add(tenant_user)

        session.commit()
        print("Seeding completed successfully! Demo gym 'Iron Peak Fitness' and tenant gym 'City Fit Club' ready.")


if __name__ == "__main__":
    seed_database()
