import os
import sys
import numpy as np
from datetime import datetime, timedelta

# Set python path to find app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal, Base, engine
from app.models import Child, HealthRecord, FollowUp
from app.ml.who_standards import calculate_z_scores, classify_nutritional_status

# Clean database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

np.random.seed(123)

villages = [
    ("Shamshabad", "Rangareddy", "Telangana"),
    ("Nalgonda", "Nalgonda", "Telangana"),
    ("Najafgarh", "South West Delhi", "Delhi"),
    ("Bhatinda", "Bhatinda", "Punjab"),
    ("Medak", "Medak", "Telangana"),
    ("Karimnagar", "Karimnagar", "Telangana")
]

names = [
    ("Aarav", "Male"), ("Ishaan", "Male"), ("Vihaan", "Male"), ("Aditya", "Male"), ("Arjun", "Male"),
    ("Sai", "Male"), ("Rahul", "Male"), ("Krishna", "Male"), ("Charan", "Male"), ("Vicky", "Male"),
    ("Ananya", "Female"), ("Diya", "Female"), ("Saanvi", "Female"), ("Aanya", "Female"), ("Prisha", "Female"),
    ("Meera", "Female"), ("Jyothi", "Female"), ("Saritha", "Female"), ("Divya", "Female"), ("Kavya", "Female"),
    ("Rohan", "Male"), ("Karan", "Male"), ("Kriti", "Female"), ("Sneha", "Female"), ("Abhay", "Male")
]

incomes = ["Low", "Medium", "High"]
diets = ["Poor", "Adequate", "Good"]

print("Seeding children database...")

for idx, (name, gender) in enumerate(names):
    # Demographics
    vil, dist, state = villages[idx % len(villages)]
    income = np.random.choice(incomes, p=[0.5, 0.4, 0.1])
    # Age between 6 and 48 months
    age = float(np.random.randint(6, 48))
    
    child = Child(
        name=name,
        gender=gender,
        age_months=age,
        family_income=income,
        village=vil,
        district=dist,
        state=state
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    
    # We will generate 3 health records logged at 2-month intervals
    # To show history, we subtract 4 months and 2 months for the past records
    status_type = np.random.choice(["Normal", "Mild", "Moderate", "Severe"], p=[0.4, 0.3, 0.2, 0.1])
    
    for record_idx in range(3):
        months_ago = (2 - record_idx) * 2
        record_age = age - months_ago
        
        # Calculate measurements with some growth trends
        # Normal, improving, or stagnant
        if status_type == "Normal":
            z_w = np.random.uniform(-0.8, 0.8)
            z_h = np.random.uniform(-0.8, 0.8)
            muac = np.random.uniform(13.8, 15.5)
            hb = np.random.uniform(11.5, 13.5)
            diet = "Good" if income != "Low" else "Adequate"
        elif status_type == "Mild":
            z_w = np.random.uniform(-1.8, -1.1)
            z_h = np.random.uniform(-1.8, -1.1)
            muac = np.random.uniform(12.6, 13.3)
            hb = np.random.uniform(10.2, 11.2)
            diet = "Adequate"
        elif status_type == "Moderate":
            # Show a recovery trend for some children
            trend_improvement = record_idx * 0.4
            z_w = np.random.uniform(-2.8, -2.1) + trend_improvement
            z_h = np.random.uniform(-2.8, -2.1) + trend_improvement / 2.0
            muac = np.random.uniform(11.6, 12.3) + trend_improvement * 0.5
            hb = np.random.uniform(8.5, 10.2) + trend_improvement * 0.8
            diet = "Poor" if record_idx == 0 else "Adequate"
        else: # Severe
            # Stagnant malnutrition
            z_w = np.random.uniform(-3.8, -3.1)
            z_h = np.random.uniform(-3.8, -3.1)
            muac = np.random.uniform(9.5, 11.2)
            hb = np.random.uniform(5.5, 7.8)
            diet = "Poor"

        # WHO lookups
        from app.ml.who_standards import interpolate_standard
        w_med, w_sd = interpolate_standard(gender, "weight_for_age", record_age)
        h_med, h_sd = interpolate_standard(gender, "height_for_age", record_age)
        
        weight = float(w_med + z_w * w_sd)
        height = float(h_med + z_h * h_sd)
        
        z_scores = calculate_z_scores(weight, height, record_age, gender)
        status, risk = classify_nutritional_status(z_scores, muac, hb)
        
        rec_time = datetime.utcnow() - timedelta(days=months_ago * 30)
        
        record = HealthRecord(
            child_id=child.id,
            weight_kg=round(weight, 2),
            height_cm=round(height, 1),
            muac_cm=round(muac, 1),
            hemoglobin_gdl=round(hb, 1),
            dietary_habits=diet,
            wasting_z=round(z_scores["wasting_z"], 2),
            stunting_z=round(z_scores["stunting_z"], 2),
            underweight_z=round(z_scores["underweight_z"], 2),
            status=status,
            risk_score=risk,
            recorded_at=rec_time
        )
        db.add(record)
        db.commit()

        # If it is the last record and child is malnourished, add a follow-up alert scheduled in the future
        if record_idx == 2 and status in ["Moderate Malnutrition", "Severe Malnutrition"]:
            days_offset = 7 if status == "Severe Malnutrition" else 14
            next_date = datetime.utcnow().date() + timedelta(days=days_offset)
            
            followup = FollowUp(
                child_id=child.id,
                scheduled_date=next_date,
                notes=f"Follow-up check-up for {status} child."
            )
            db.add(followup)
            db.commit()

print("Successfully seeded 25 children with historical health records!")
db.close()
