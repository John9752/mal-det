def get_nutrition_recommendations(status: str, age_months: float, weight_kg: float, state: str):
    """
    Computes daily dietary requirements and suggests cheap, locally available foods
    based on Indian regional habits and malnutrition status.
    """
    # 1. Compute target calories and proteins (ICMR / WHO guidelines)
    # Normal: ~90-100 kcal/kg, ~1.2g protein/kg
    # Mild/Moderate: ~120-130 kcal/kg, ~1.5-2.0g protein/kg
    # Severe: ~150-180 kcal/kg, ~2.5-3.0g protein/kg (Requires therapeutic food)
    
    if status == "Severe Malnutrition":
        calories_per_kg = 150.0
        protein_per_kg = 2.5
    elif status == "Moderate Malnutrition":
        calories_per_kg = 130.0
        protein_per_kg = 2.0
    elif status == "Mild Malnutrition":
        calories_per_kg = 110.0
        protein_per_kg = 1.6
    else:
        calories_per_kg = 95.0
        protein_per_kg = 1.2
        
    required_calories = round(weight_kg * calories_per_kg, 0)
    required_protein = round(weight_kg * protein_per_kg, 1)

    # 2. Determine Indian Region based on State
    south_states = ["andhra pradesh", "andhrapradesh", "telangana", "tamil nadu", "tamillnadu", "karnataka", "kerala", "pondicherry"]
    north_states = ["delhi", "punjab", "haryana", "uttar pradesh", "uttarpradesh", "himachal pradesh", "himachalpradesh", "jammu", "kashmir", "uttarakhand"]
    east_states = ["west bengal", "westbengal", "bihar", "odisha", "jharkhand", "assam", "tripura", "manipur", "meghalaya", "mizoram", "nagaland", "arunachal pradesh", "arunachalpradesh", "sikkim"]
    
    state_lower = state.lower().strip()
    if any(s in state_lower for s in south_states):
        region = "South India"
    elif any(s in state_lower for s in north_states):
        region = "North India"
    elif any(s in state_lower for s in east_states):
        region = "East India"
    else:
        region = "West & Central India"

    # Food recommendations by region
    regional_foods = {
        "South India": [
            {"food": "Ragi (Finger Millet) Kanji/Porridge", "benefits": "Extremely rich in Calcium and Iron, easy to digest.", "cost": "Very Low"},
            {"food": "Mashed Idli with Ghee and Dal", "benefits": "High protein, carbohydrates, and healthy fats from ghee.", "cost": "Low"},
            {"food": "Moringa (Drumstick) Leaf Lentil Soup (Sambar)", "benefits": "Moringa is packed with Vitamin A, Vitamin C, Iron, and protein.", "cost": "Very Low"},
            {"food": "Boiled Egg (daily or alternate days)", "benefits": "Highest quality protein, essential fats, and Vitamin B12.", "cost": "Low"},
            {"food": "Peanut Chikki / Roasted Chana", "benefits": "Excellent source of energy, healthy unsaturated fats, and plant protein.", "cost": "Low"},
            {"food": "Banana (Elakki or Robusta)", "benefits": "Instant calories, Potassium, and dietary fiber.", "cost": "Very Low"}
        ],
        "North India": [
            {"food": "Roasted Chana Sattu drink / paste", "benefits": "Superfood with very high protein content and cooling properties.", "cost": "Very Low"},
            {"food": "Moong Dal Khichdi with Ghee and carrots", "benefits": "Perfect balance of amino acids (rice + lentils) and Vitamin A.", "cost": "Low"},
            {"food": "Wheat Daliya (Broken Wheat Porridge) with Milk", "benefits": "High energy, dietary fiber, and essential minerals.", "cost": "Low"},
            {"food": "Mashed Potato & Green Peas with butter", "benefits": "High calorie density to boost weight gain rapidly.", "cost": "Very Low"},
            {"food": "Curd (Dahi) or Butter Milk (Lassi)", "benefits": "Rich in Calcium, protein, and probiotics for gut health.", "cost": "Low"},
            {"food": "Boiled Egg", "benefits": "High bioavailability protein and fats for tissue building.", "cost": "Low"}
        ],
        "East India": [
            {"food": "Mashed Rice with Musur Dal and ghee", "benefits": "Easily digestible source of energy and protein.", "cost": "Very Low"},
            {"food": "Sattu porridge (roasted barley/gram)", "benefits": "High protein and iron, very cost-effective.", "cost": "Very Low"},
            {"food": "Mashed Sweet Potato (Sakar Kanda)", "benefits": "Dense calories and highly rich in Vitamin A (Beta-carotene).", "cost": "Very Low"},
            {"food": "Small local Fish curry (if non-vegetarian)", "benefits": "Rich in Omega-3 fatty acids, high-quality protein, and minerals.", "cost": "Medium-Low"},
            {"food": "Boiled Egg", "benefits": "Provides critical amino acids for growth.", "cost": "Low"},
            {"food": "Mashed Banana", "benefits": "High calorie density and simple carbohydrates.", "cost": "Very Low"}
        ],
        "West & Central India": [
            {"food": "Nachni (Ragi) Bhakri with ghee", "benefits": "Rich in Calcium and Iron, supports bone density.", "cost": "Low"},
            {"food": "Sprouted Moong Usal / paste", "benefits": "Sprouting increases Vitamin C and bioavailability of protein/iron.", "cost": "Low"},
            {"food": "Peanut Chikki / Sesame (Til) Laddoo", "benefits": "High calories, healthy fats, iron, and minerals.", "cost": "Low"},
            {"food": "Khichdi with mixed green leafy vegetables", "benefits": "Provides proteins, carbs, Iron, and Vitamin A.", "cost": "Very Low"},
            {"food": "Cow's Milk or Dahi", "benefits": "Essential Calcium and protein for growing children.", "cost": "Medium-Low"},
            {"food": "Banana or Guava", "benefits": "Local vitamins (C, A) and calorie density.", "cost": "Very Low"}
        ]
    }
    
    general_guidelines = []
    if status == "Severe Malnutrition":
        general_guidelines = [
            "IMMEDIATE ACTION REQUIRED: Refer the child to the nearest Nutrition Rehabilitation Centre (NRC).",
            "Administer Ready-to-Use Therapeutic Food (RUTF) or F-75 / F-100 therapeutic milk under medical supervision.",
            "Avoid force-feeding; feed small quantities frequently (every 2 hours).",
            "Monitor body temperature and watch for signs of lethargy, diarrhea, or fever."
        ]
    elif status == "Moderate Malnutrition":
        general_guidelines = [
            "Increase feeding frequency to 5-6 times a day.",
            "Add 1-2 teaspoons of Ghee, Butter, or Oil to every meal to increase calorie density.",
            "Ensure the child consumes at least one protein source (egg, lentils, dairy, or fish) daily.",
            "Enroll the child in the local Anganwadi's Supplementary Nutrition Program (SNP)."
        ]
    elif status == "Mild Malnutrition":
        general_guidelines = [
            "Ensure 3 main meals and 2 nutritious snacks per day.",
            "Include colorful vegetables and local seasonal fruits to combat micronutrient deficits.",
            "Verify immunization schedule is up to date and deworming tablet has been administered."
        ]
    else:
        general_guidelines = [
            "Maintain a balanced diet including carbohydrates, proteins, fats, and vitamins.",
            "Promote handwashing before meals and hygienic food preparation.",
            "Schedule standard half-yearly growth monitoring at the Anganwadi centre."
        ]

    return {
        "required_calories": required_calories,
        "required_protein_g": required_protein,
        "region": region,
        "food_recommendations": regional_foods.get(region, regional_foods["South India"]),
        "clinical_guidelines": general_guidelines
    }


def get_scheme_recommendations(age_months: float, gender: str, status: str, income: str, state: str):
    """
    Checks child parameters against eligibility rules for major Indian nutrition and welfare schemes.
    """
    schemes = []

    # 1. ICDS - Integrated Child Development Services / Anganwadi Services
    # Eligible: All children 0-6 years (0-72 months)
    if age_months <= 72.0:
        benefits = "Provides Supplementary Nutrition (Take Home Ration - THR for 6-36 months, Hot Cooked Meals for 3-6 years), immunization, health checkups, and early childhood non-formal education."
        if status in ["Moderate Malnutrition", "Severe Malnutrition"]:
            benefits += " Eligible for DOUBLE supplementary nutrition ration under SAM/MAM guidelines."
        schemes.append({
            "name": "Integrated Child Development Services (ICDS) / Anganwadi Services",
            "ministry": "Ministry of Women and Child Development",
            "eligibility": "Children under 6 years, pregnant and lactating mothers.",
            "benefits": benefits,
            "how_to_apply": "Visit your nearest local Anganwadi worker/centre with child's Aadhar Card and Birth Certificate."
        })

    # 2. POSHAN Abhiyaan (National Nutrition Mission)
    # Target: Stunting, Under-nutrition, Anemia in children 0-6 years
    if age_months <= 72.0:
        schemes.append({
            "name": "POSHAN Abhiyaan (National Nutrition Mission)",
            "ministry": "Ministry of Women and Child Development",
            "eligibility": "Children under 6 years, adolescent girls, pregnant/lactating women.",
            "benefits": "Focused growth monitoring (using Poshan Tracker), counseling, micronutrient supplementation (Iron-Folic Acid, Vitamin A), and deworming.",
            "how_to_apply": "Automatic enrollment through Anganwadi Center registration."
        })

    # 3. PM Matru Vandana Yojana (PMMVY)
    # Pregnant and lactating mothers for first child (or second child if girl)
    # Useful for infants under 1 year (12 months)
    if age_months <= 12.0:
        schemes.append({
            "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
            "ministry": "Ministry of Women and Child Development",
            "eligibility": "Pregnant and lactating mothers for the first living child in the family.",
            "benefits": "Cash incentive of ₹5,000 in three installments directly into the bank account to compensate for wage loss and support nutrition.",
            "how_to_apply": "Apply through the Anganwadi Center or online on the PMMVY portal within 150 days of pregnancy registration."
        })

    # 4. PM POSHAN (Mid-Day Meal Scheme)
    # Eligible: Children attending classes I to VIII (typically aged 6-14 years, i.e., >72 months)
    if age_months > 72.0:
        schemes.append({
            "name": "PM POSHAN (Mid-Day Meal Scheme)",
            "ministry": "Ministry of Education",
            "eligibility": "Children studying in classes I to VIII in Government, Government-aided, and Local Body schools.",
            "benefits": "Free hot cooked nutritious lunch every day with guaranteed 450 calories and 12g protein (for primary) and 700 calories/20g protein (for upper primary).",
            "how_to_apply": "Automatic benefit upon enrollment in government-run schools."
        })

    # 5. Balri Suraksha Yojana (State-Specific - targeting girl child and family planning)
    if gender == "Female" and income == "Low":
        schemes.append({
            "name": "Balri Suraksha Yojana (Financial Aid)",
            "ministry": "Department of Social Security, Women and Child Development",
            "eligibility": "Families with only single or two girl children who have adopted terminal family planning methods.",
            "benefits": "Monthly financial aid of ₹500 per girl child until they reach 18 years to assist with nutrition and education.",
            "how_to_apply": "Submit application to the District Social Security Officer (DSSO) or Anganwadi Supervisor."
        })
        
    # 6. Specific Nutritional rehabilitation for SAM (Severe Acute Malnutrition)
    if status == "Severe Malnutrition":
        schemes.append({
            "name": "Nutrition Rehabilitation Centre (NRC) Admission",
            "ministry": "Ministry of Health and Family Welfare (National Health Mission)",
            "eligibility": "Children diagnosed with Severe Acute Malnutrition (SAM) showing medical complications.",
            "benefits": "14-day free inpatient care, specialized therapeutic feeding (F-75/F-100), daily doctor check-up, wage compensation for mothers (approx. ₹150-250/day), and follow-up checks.",
            "how_to_apply": "Immediate referral by Anganwadi Worker (AWW) or Auxiliary Nurse Midwife (ANM) to nearest Community Health Centre (CHC) or District Hospital."
        })

    # 7. Arogya Lakshmi (Telangana specific - generic check for state)
    state_lower = state.lower().strip()
    if "telangana" in state_lower or "andhra" in state_lower:
        schemes.append({
            "name": "Arogya Lakshmi Scheme",
            "ministry": "State Department of Women & Child Development",
            "eligibility": "Pregnant women, lactating mothers, and children under 6 years in Telangana/AP.",
            "benefits": "One full nutritious meal consisting of rice, dal, vegetables, boiled egg, and milk (200ml) served daily at Anganwadi centers.",
            "how_to_apply": "Enroll at the local village Anganwadi center."
        })

    return schemes
