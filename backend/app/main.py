from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import os
import shutil
import pickle
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg') # Set non-interactive backend for server environment
import matplotlib.pyplot as plt

from .database import engine, Base, get_db
from .models import Child, HealthRecord, FollowUp, User
from .schemas import (
    ChildCreate, ChildResponse, HealthRecordResponse, FollowUpResponse,
    ChildDetailResponse, UserRegister, UserLogin, UserResponse, TokenResponse, UserSync
)
from .firebase_auth import get_current_firebase_user
from .ml.who_standards import calculate_z_scores, classify_nutritional_status, interpolate_standard
from .ml.image_processor import analyze_child_image
from .ml.recommendations import get_nutrition_recommendations, get_scheme_recommendations
from fastapi.responses import StreamingResponse
from .reports import generate_child_health_card_pdf

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Malnutrition Detection System")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load ML Model & Scaler if available
MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml")
model_path = os.path.join(MODEL_DIR, "best_model.pkl")
scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")

ml_model = None
scaler = None

if os.path.exists(model_path) and os.path.exists(scaler_path):
    try:
        with open(model_path, "rb") as f:
            ml_model = pickle.load(f)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        print("ML Model and Scaler loaded successfully.")
    except Exception as e:
        print(f"Error loading ML model: {e}")


@app.get("/")
def read_root():
    return {"message": "Malnutrition Detection API is running"}


# --- AUTH ENDPOINTS ---

@app.post("/api/auth/sync", response_model=UserResponse)
def sync_user(data: UserSync, db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    if data.uid != current_fb_user["uid"]:
        raise HTTPException(status_code=403, detail="Unauthorized user sync request")

    user = db.query(User).filter(User.id == data.uid).first()
    if not user:
        user = User(
            id=data.uid,
            full_name=data.full_name,
            email=data.email,
            center_name=data.center_name
        )
        db.add(user)
    else:
        user.full_name = data.full_name
        if data.center_name:
            user.center_name = data.center_name
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    user = db.query(User).filter(User.id == current_fb_user["uid"]).first()
    if not user:
        # Create a user profile on the fly if verified but not synced yet
        user = User(
            id=current_fb_user["uid"],
            full_name=current_fb_user.get("name") or current_fb_user["email"].split("@")[0],
            email=current_fb_user["email"],
            center_name=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# --- CHILD ENDPOINTS ---

@app.post("/api/children", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(child: ChildCreate, db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    # Ensure local user profile exists
    local_user = db.query(User).filter(User.id == current_fb_user["uid"]).first()
    if not local_user:
        local_user = User(
            id=current_fb_user["uid"],
            full_name=current_fb_user.get("name") or current_fb_user["email"].split("@")[0],
            email=current_fb_user["email"],
            center_name=None
        )
        db.add(local_user)
        db.commit()
        db.refresh(local_user)

    db_child = Child(
        name=child.name,
        gender=child.gender,
        age_months=child.age_months,
        family_income=child.family_income,
        village=child.village,
        district=child.district,
        state=child.state,
        worker_id=local_user.id
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child


@app.get("/api/children", response_model=list[ChildResponse])
def get_children(db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    return db.query(Child).filter(Child.worker_id == current_fb_user["uid"]).order_by(Child.created_at.desc()).all()


@app.get("/api/children/{child_id}", response_model=ChildDetailResponse)
def get_child_detail(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    return child


# --- HEALTH RECORD & PREDICTION ENDPOINTS ---

@app.post("/api/children/{child_id}/records", response_model=HealthRecordResponse)
async def add_health_record(
    child_id: int,
    weight_kg: float = Form(...),
    height_cm: float = Form(...),
    muac_cm: float = Form(...),
    hemoglobin_gdl: float = Form(None),
    dietary_habits: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # 1. Save uploaded image if any
    saved_img_path = None
    image_risk = 0.0
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        filename = f"child_{child_id}_{int(datetime.utcnow().timestamp())}{file_ext}"
        saved_img_path = os.path.join(UPLOAD_DIR, filename)
        with open(saved_img_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Analyze using OpenCV
        cv_results = analyze_child_image(saved_img_path)
        if cv_results["face_detected"]:
            image_risk = cv_results["image_risk_score"]

    # Update child age to matches record date relative to birth,
    # but for simplicity we'll use child's current age.
    age = child.age_months

    # 2. Compute WHO Z-scores
    z_scores = calculate_z_scores(weight_kg, height_cm, age, child.gender)

    # 3. Predict Malnutrition Status
    # Standard classification
    clinical_status, clinical_risk = classify_nutritional_status(z_scores, muac_cm, hemoglobin_gdl)

    # If ML model is loaded, predict with ML model
    predicted_status = clinical_status
    predicted_risk = clinical_risk

    if ml_model and scaler:
        try:
            gender_code = 0 if child.gender == "Male" else 1
            income_code = 0 if child.family_income == "Low" else (1 if child.family_income == "Medium" else 2)
            diet_code = 0 if dietary_habits == "Poor" else (1 if dietary_habits == "Adequate" else 2)
            hb_val = hemoglobin_gdl if hemoglobin_gdl is not None else 12.0

            # Scale and Predict
            features = np.array([[
                age, gender_code, weight_kg, height_cm, muac_cm, hb_val, diet_code, income_code, image_risk
            ]])
            features_scaled = scaler.transform(features)
            
            ml_pred_class = ml_model.predict(features_scaled)[0]
            ml_prob = ml_model.predict_proba(features_scaled)[0]
            
            # Map classes: 0 -> Normal, 1 -> Mild, 2 -> Moderate, 3 -> Severe
            status_map = {
                0: "Normal",
                1: "Mild Malnutrition",
                2: "Moderate Malnutrition",
                3: "Severe Malnutrition"
            }
            predicted_status = status_map[ml_pred_class]
            
            # Risk calculation based on probability distributions
            # Sum probability of malnutrition classes weighted by severity
            ml_risk = (ml_prob[1] * 35) + (ml_prob[2] * 70) + (ml_prob[3] * 100)
            
            # Blend ML risk and Clinical Z-score risk
            predicted_risk = round(0.4 * clinical_risk + 0.6 * ml_risk, 1)

        except Exception as e:
            print(f"ML Prediction failed, using WHO Z-score: {e}")

    # Ensure risk score is formatted correctly
    predicted_risk = min(100.0, max(0.0, predicted_risk))

    # 4. Save Health Record
    record = HealthRecord(
        child_id=child_id,
        weight_kg=weight_kg,
        height_cm=height_cm,
        muac_cm=muac_cm,
        hemoglobin_gdl=hemoglobin_gdl,
        dietary_habits=dietary_habits,
        image_path=saved_img_path,
        wasting_z=z_scores["wasting_z"],
        stunting_z=z_scores["stunting_z"],
        underweight_z=z_scores["underweight_z"],
        status=predicted_status,
        risk_score=predicted_risk
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 5. Alert Trigger & Schedule Follow-ups for MAM/SAM children
    if predicted_status in ["Moderate Malnutrition", "Severe Malnutrition"]:
        # Schedule next checkup: weekly for SAM, bi-weekly for MAM
        days_offset = 7 if predicted_status == "Severe Malnutrition" else 14
        next_date = date.today() + timedelta(days=days_offset)
        
        # Check if follow-up already scheduled
        existing_followup = db.query(FollowUp).filter(
            FollowUp.child_id == child_id,
            FollowUp.completed == False
        ).first()

        if not existing_followup:
            followup = FollowUp(
                child_id=child_id,
                scheduled_date=next_date,
                notes=f"Auto-generated checkup for {predicted_status} child."
            )
            db.add(followup)
            db.commit()

    return record


# --- RECOMMENDATION ENDPOINTS ---

@app.get("/api/children/{child_id}/recommendations")
def get_recommendations(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    last_record = db.query(HealthRecord).filter(
        HealthRecord.child_id == child_id
    ).order_by(HealthRecord.recorded_at.desc()).first()

    if not last_record:
        raise HTTPException(status_code=400, detail="No health records logged for this child yet")

    nutrition = get_nutrition_recommendations(
        last_record.status, child.age_months, last_record.weight_kg, child.state
    )
    schemes = get_scheme_recommendations(
        child.age_months, child.gender, last_record.status, child.family_income, child.state
    )

    return {
        "child_name": child.name,
        "status": last_record.status,
        "risk_score": last_record.risk_score,
        "nutrition": nutrition,
        "schemes": schemes
    }


# --- GROWTH CHARTS ENDPOINT (Matplotlib base64 export) ---

@app.get("/api/children/{child_id}/growth-chart")
def get_growth_chart(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    records = db.query(HealthRecord).filter(
        HealthRecord.child_id == child_id
    ).order_by(HealthRecord.recorded_at.asc()).all()

    if not records:
        raise HTTPException(status_code=400, detail="No health records logged for this child yet")

    # Generate Weight-for-Age and Height-for-Age curves
    gender = child.gender
    ages = np.linspace(0, 60, 100)
    
    # 1. Weight Chart
    plt.figure(figsize=(8, 5))
    
    # WHO bands
    w_med_curve = []
    w_sd_plus2 = []
    w_sd_minus2 = []
    w_sd_minus3 = []
    
    for a in ages:
        m, sd = interpolate_standard(gender, "weight_for_age", a)
        w_med_curve.append(m)
        w_sd_plus2.append(m + 2 * sd)
        w_sd_minus2.append(m - 2 * sd)
        w_sd_minus3.append(m - 3 * sd)

    plt.plot(ages, w_med_curve, label="WHO Median", color="green", linestyle="--")
    plt.plot(ages, w_sd_plus2, label="+2 SD (Overweight Threshold)", color="orange", linestyle=":")
    plt.plot(ages, w_sd_minus2, label="-2 SD (Underweight Threshold)", color="orange", linestyle=":")
    plt.plot(ages, w_sd_minus3, label="-3 SD (Severely Underweight)", color="red", linestyle="-.")
    
    plt.fill_between(ages, w_sd_minus2, w_sd_plus2, color="green", alpha=0.08, label="Healthy Range")
    plt.fill_between(ages, w_sd_minus3, w_sd_minus2, color="orange", alpha=0.1, label="Moderate Underweight")
    
    # Child's logged data
    child_ages = [r.recorded_at.microsecond % 60 + child.age_months for r in records] # Simulate age progression for demo
    # We will compute age in months relative to history or just increment by 2 months per record for visualization
    sim_ages = []
    curr_age = child.age_months - (len(records) - 1) * 2
    for i in range(len(records)):
        sim_ages.append(max(0.0, curr_age + i * 2))

    child_weights = [r.weight_kg for r in records]
    plt.scatter(sim_ages, child_weights, color="#4f46e5", s=80, zorder=5)
    plt.plot(sim_ages, child_weights, color="#4f46e5", linewidth=3, label=f"{child.name}'s Profile")
    
    plt.title(f"Weight-for-Age Growth Chart ({child.gender})", fontsize=12, fontweight='bold', pad=10)
    plt.xlabel("Age (Months)")
    plt.ylabel("Weight (Kg)")
    plt.legend(loc="upper left", frameon=True, fontsize=9)
    plt.grid(True, linestyle=":", alpha=0.5)
    
    # Save Weight to base64
    buf_w = io.BytesIO()
    plt.savefig(buf_w, format='png', dpi=120)
    buf_w.seek(0)
    img_w_b64 = base64.b64encode(buf_w.read()).decode('utf-8')
    plt.close()

    # 2. Height Chart
    plt.figure(figsize=(8, 5))
    
    h_med_curve = []
    h_sd_plus2 = []
    h_sd_minus2 = []
    h_sd_minus3 = []
    
    for a in ages:
        m, sd = interpolate_standard(gender, "height_for_age", a)
        h_med_curve.append(m)
        h_sd_plus2.append(m + 2 * sd)
        h_sd_minus2.append(m - 2 * sd)
        h_sd_minus3.append(m - 3 * sd)

    plt.plot(ages, h_med_curve, label="WHO Median", color="green", linestyle="--")
    plt.plot(ages, h_sd_plus2, label="+2 SD (Tall)", color="orange", linestyle=":")
    plt.plot(ages, h_sd_minus2, label="-2 SD (Stunted Threshold)", color="orange", linestyle=":")
    plt.plot(ages, h_sd_minus3, label="-3 SD (Severely Stunted)", color="red", linestyle="-.")
    
    plt.fill_between(ages, h_sd_minus2, h_sd_plus2, color="green", alpha=0.08, label="Healthy Range")
    plt.fill_between(ages, h_sd_minus3, h_sd_minus2, color="orange", alpha=0.1, label="Moderate Stunting")
    
    child_heights = [r.height_cm for r in records]
    plt.scatter(sim_ages, child_heights, color="#4f46e5", s=80, zorder=5)
    plt.plot(sim_ages, child_heights, color="#4f46e5", linewidth=3, label=f"{child.name}'s Profile")
    
    plt.title(f"Height-for-Age Growth Chart ({child.gender})", fontsize=12, fontweight='bold', pad=10)
    plt.xlabel("Age (Months)")
    plt.ylabel("Height (Cm)")
    plt.legend(loc="upper left", frameon=True, fontsize=9)
    plt.grid(True, linestyle=":", alpha=0.5)
    
    buf_h = io.BytesIO()
    plt.savefig(buf_h, format='png', dpi=120)
    buf_h.seek(0)
    img_h_b64 = base64.b64encode(buf_h.read()).decode('utf-8')
    plt.close()

    return {
        "weight_chart_b64": img_w_b64,
        "height_chart_b64": img_h_b64
    }


# --- PDF REPORT GENERATION ENDPOINT ---

@app.get("/api/children/{child_id}/report")
def get_child_report(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
        
    last_record = db.query(HealthRecord).filter(
        HealthRecord.child_id == child_id
    ).order_by(HealthRecord.recorded_at.desc()).first()
    
    if not last_record:
        raise HTTPException(status_code=400, detail="No health records logged for this child yet")
        
    # Generate recommendations & schemes
    nutrition = get_nutrition_recommendations(
        last_record.status, child.age_months, last_record.weight_kg, child.state
    )
    schemes = get_scheme_recommendations(
        child.age_months, child.gender, last_record.status, child.family_income, child.state
    )
    
    pdf_buffer = generate_child_health_card_pdf(child, last_record, nutrition, schemes)
    
    filename = f"health_card_{child.name.replace(' ', '_')}_{child_id}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# --- ANALYTICS DASHBOARD ENDPOINT ---

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    total_children = db.query(Child).filter(Child.worker_id == current_fb_user["uid"]).count()
    
    # MALNUTRITION DISTRIBUTION
    # Get last record for each child belonging to this worker
    subq = db.query(
        HealthRecord.child_id,
        HealthRecord.status,
        HealthRecord.risk_score,
        HealthRecord.wasting_z,
        HealthRecord.stunting_z,
        HealthRecord.underweight_z,
        HealthRecord.recorded_at
    ).join(Child, HealthRecord.child_id == Child.id)\
     .filter(Child.worker_id == current_fb_user["uid"])\
     .order_by(HealthRecord.recorded_at.desc()).all()
    
    # Deduplicate in Python to get latest status per child
    latest_records = {}
    for r in subq:
        if r.child_id not in latest_records:
            latest_records[r.child_id] = r
            
    status_counts = {"Normal": 0, "Mild Malnutrition": 0, "Moderate Malnutrition": 0, "Severe Malnutrition": 0}
    wasted_count = 0
    stunted_count = 0
    underweight_count = 0
    total_anemic = 0
    
    for r in latest_records.values():
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
        if r.wasting_z and r.wasting_z <= -2.0:
            wasted_count += 1
        if r.stunting_z and r.stunting_z <= -2.0:
            stunted_count += 1
        if r.underweight_z and r.underweight_z <= -2.0:
            underweight_count += 1
            
    # ANEMIA COUNTS
    anemia_records = db.query(HealthRecord.hemoglobin_gdl)\
                       .join(Child, HealthRecord.child_id == Child.id)\
                       .filter(Child.worker_id == current_fb_user["uid"], HealthRecord.hemoglobin_gdl != None).all()
    for ar in anemia_records:
        if ar.hemoglobin_gdl < 11.0:
            total_anemic += 1
            
    # AGE & GENDER DISTRIBUTION
    children = db.query(Child).filter(Child.worker_id == current_fb_user["uid"]).all()
    gender_counts = {"Male": 0, "Female": 0}
    age_groups = {"0-12m": 0, "12-36m": 0, "36-60m": 0}
    
    for c in children:
        gender_counts[c.gender] = gender_counts.get(c.gender, 0) + 1
        if c.age_months <= 12:
            age_groups["0-12m"] += 1
        elif c.age_months <= 36:
            age_groups["12-36m"] += 1
        else:
            age_groups["36-60m"] += 1

    # VILLAGE HEATMAP AGGREGATES
    # Group children by village
    villages = db.query(Child.village, Child.district, Child.state).distinct().all()
    village_data = []
    
    # Reference coordinates for demo (centered in Telangana, India: 17.3850, 78.4867)
    base_lat, base_lng = 17.3850, 78.4867
    
    for idx, vil in enumerate(villages):
        v_name, v_dist, v_state = vil
        # Get children in this village
        v_children = db.query(Child.id).filter(Child.village == v_name).all()
        v_child_ids = [c.id for c in v_children]
        
        # Count statuses in this village
        v_cases = 0
        v_total = len(v_child_ids)
        for cid in v_child_ids:
            if cid in latest_records and latest_records[cid].status in ["Moderate Malnutrition", "Severe Malnutrition"]:
                v_cases += 1
                
        # Generate coordinates offset slightly to scatter them
        lat = base_lat + (idx % 3 - 1.5) * 0.05 + np.sin(idx) * 0.02
        lng = base_lng + (idx % 2 - 1.0) * 0.05 + np.cos(idx) * 0.02
        
        village_data.append({
            "name": v_name,
            "district": v_dist,
            "state": v_state,
            "lat": lat,
            "lng": lng,
            "total_children": v_total,
            "malnourished_cases": v_cases,
            "intensity": (v_cases / v_total) if v_total > 0 else 0.0
        })

    # HIGH RISK ALERTS SUMMARY
    high_risk_list = []
    for cid, r in latest_records.items():
        if r.status in ["Moderate Malnutrition", "Severe Malnutrition"]:
            c_info = db.query(Child).filter(Child.id == cid).first()
            if c_info:
                high_risk_list.append({
                    "child_id": c_info.id,
                    "name": c_info.name,
                    "gender": c_info.gender,
                    "age_months": c_info.age_months,
                    "village": c_info.village,
                    "status": r.status,
                    "risk_score": r.risk_score
                })

    return {
        "kpis": {
            "total_registered": total_children,
            "sam_cases": status_counts["Severe Malnutrition"],
            "mam_cases": status_counts["Moderate Malnutrition"],
            "anemia_cases": total_anemic,
            "wasting_rate": round(wasted_count / max(1, len(latest_records)) * 100, 1),
            "stunting_rate": round(stunted_count / max(1, len(latest_records)) * 100, 1),
            "underweight_rate": round(underweight_count / max(1, len(latest_records)) * 100, 1)
        },
        "malnutrition_distribution": status_counts,
        "gender_distribution": gender_counts,
        "age_distribution": age_groups,
        "villages": village_data,
        "high_risk_list": high_risk_list[:10] # Top 10 high risk children
    }


# --- ALERT & FOLLOW-UP ENDPOINTS ---

@app.get("/api/alerts", response_model=list[FollowUpResponse])
def get_alerts(db: Session = Depends(get_db), current_fb_user: dict = Depends(get_current_firebase_user)):
    return (
        db.query(FollowUp)
        .join(Child, FollowUp.child_id == Child.id)
        .filter(Child.worker_id == current_fb_user["uid"], FollowUp.completed == False)
        .order_by(FollowUp.scheduled_date.asc())
        .all()
    )


@app.post("/api/alerts/{alert_id}/complete")
def complete_alert(alert_id: int, notes: str = Form(None), db: Session = Depends(get_db)):
    followup = db.query(FollowUp).filter(FollowUp.id == alert_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Alert/FollowUp not found")
        
    followup.completed = True
    if notes:
        followup.notes = notes
    db.commit()
    return {"message": "Follow-up alert completed successfully"}


# --- RE-TRAIN ML MODELS ROUTE ---

@app.post("/api/train")
def train_models():
    """Triggers ML training process manually."""
    try:
        from .ml.train import train_and_evaluate
        train_and_evaluate()
        
        # Re-load model after training
        global ml_model, scaler
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            with open(model_path, "rb") as f:
                ml_model = pickle.load(f)
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
                
        # Read the generated report
        report_path = os.path.join(MODEL_DIR, "model_report.md")
        report_data = "Model report generated successfully."
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_data = f.read()

        return {
            "status": "success",
            "message": "Models trained successfully and updated in application context.",
            "report": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training process failed: {str(e)}")


# --- VOICE ASSISTANT ENDPOINT (Online Indic Transcriber & Guidance) ---

@app.post("/api/voice/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Simulates online speech-to-text (STT) and NLU entity extraction in five Indic languages:
    Hindi, Telugu, Tamil, Bengali, and English.
    """
    # Verify file is received
    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is required")

    # Read bytes to simulate upload processing
    audio_data = await audio.read()
    
    # Custom Indic Responses for Demo
    voice_responses = {
        "te": {
            "text": "బాబు పేరు ఆరవ్, బరువు తొమ్మిది కిలోలు, ఎత్తు డెబ్బై ఐదు సెంటీమీటర్లు, ఎంయుఎసి పన్నెండు సెంటీమీటర్లు.",
            "extracted_entities": {
                "name": "Aarav",
                "weight_kg": 9.0,
                "height_cm": 75.0,
                "muac_cm": 12.0,
                "hemoglobin_gdl": 10.5
            },
            "voice_guidance": "బాబు ఆరవ్ కు మోడరేట్ కుపోషకహార లోపం (MAM) ఉంది. సిఫార్సు చేయబడిన ఆహారాలు: రాగి జావ, నెయ్యి అన్నం, ఉడికించిన గుడ్డు."
        },
        "hi": {
            "text": "बच्चे का नाम आरव, वजन नौ किलोग्राम, ऊंचाई पचहत्तर सेंटीमीटर, एमयूएसी बारह सेंटीमीटर।",
            "extracted_entities": {
                "name": "Aarav",
                "weight_kg": 9.0,
                "height_cm": 75.0,
                "muac_cm": 12.0,
                "hemoglobin_gdl": 10.5
            },
            "voice_guidance": "बच्चे आरव को मध्यम कुपोषण (MAM) है। अनुशंसित आहार: रागी का दलिया, दाल-खिचड़ी और उबला हुआ अंडा।"
        },
        "ta": {
            "text": "குழந்தையின் பெயர் ஆரவ், எடை ஒன்பது கிலோ, உயரம் எழுபத்தைந்து சென்டிமீட்டர், முவாக் பன்னிரண்டு சென்டிமீட்டர்.",
            "extracted_entities": {
                "name": "Aarav",
                "weight_kg": 9.0,
                "height_cm": 75.0,
                "muac_cm": 12.0,
                "hemoglobin_gdl": 10.5
            },
            "voice_guidance": "குழந்தை ஆரவ்-க்கு மிதமான ஊட்டச்சத்து குறைபாடு (MAM) உள்ளது. பரிந்துரைக்கப்படும் உணவுகள்: ராகி கஞ்சி, முருங்கைக்கீரை பருப்பு சாம்பார், வேகவைத்த முட்டை."
        },
        "bn": {
            "text": "শিশুর নাম আরভ, ওজন নয় কেজি, উচ্চতা পঁচাত্তর সেন্টিমিটার, এমইউএসি বারো সেন্টিমিটার।",
            "extracted_entities": {
                "name": "Aarav",
                "weight_kg": 9.0,
                "height_cm": 75.0,
                "muac_cm": 12.0,
                "hemoglobin_gdl": 10.5
            },
            "voice_guidance": "শিশু আরভের মাঝারি অপুষ্টি (MAM) আছে। প্রস্তাবিত খাদ্য: রাগি কাঞ্জি, মসুর ডাল দিয়ে ভাত, সেদ্ধ ডিম।"
        },
        "en": {
            "text": "Child name Aarav, weight nine kilograms, height seventy five centimeters, MUAC twelve centimeters.",
            "extracted_entities": {
                "name": "Aarav",
                "weight_kg": 9.0,
                "height_cm": 75.0,
                "muac_cm": 12.0,
                "hemoglobin_gdl": 10.5
            },
            "voice_guidance": "Child Aarav has Moderate Acute Malnutrition (MAM). Recommended foods: Ragi porridge, Dal khichdi with ghee, and a boiled egg."
        }
    }

    lang_code = language.lower().strip()
    response_data = voice_responses.get(lang_code, voice_responses["en"])

    return {
        "status": "success",
        "language_detected": lang_code,
        "transcript": response_data["text"],
        "slots_extracted": response_data["extracted_entities"],
        "guidance_audio_alert": response_data["voice_guidance"]
    }
