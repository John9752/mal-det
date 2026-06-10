import numpy as np

# WHO Child Growth Reference Data (Ages 0 to 60 months)
# format: age_months: (median_value, standard_deviation)
GROWTH_DATA = {
    "Male": {
        "weight_for_age": [
            (0, 3.3, 0.4),
            (3, 6.4, 0.6),
            (6, 7.9, 0.8),
            (9, 8.9, 0.9),
            (12, 9.6, 1.0),
            (18, 10.9, 1.15),
            (24, 12.2, 1.25),
            (30, 13.3, 1.4),
            (36, 14.3, 1.5),
            (42, 15.3, 1.65),
            (48, 16.3, 1.8),
            (54, 17.3, 1.95),
            (60, 18.3, 2.1)
        ],
        "height_for_age": [
            (0, 49.9, 2.0),
            (3, 61.4, 2.2),
            (6, 67.6, 2.5),
            (9, 72.0, 2.6),
            (12, 75.7, 2.7),
            (18, 82.3, 3.0),
            (24, 87.8, 3.2),
            (30, 92.1, 3.4),
            (36, 96.1, 3.6),
            (42, 99.9, 3.8),
            (48, 103.3, 4.0),
            (54, 106.7, 4.2),
            (60, 110.0, 4.4)
        ],
        "weight_for_height": [
            (45.0, 2.4, 0.25),
            (50.0, 3.3, 0.35),
            (55.0, 4.5, 0.45),
            (60.0, 5.7, 0.55),
            (65.0, 7.0, 0.7),
            (70.0, 8.3, 0.8),
            (75.0, 9.5, 0.9),
            (80.0, 10.4, 1.0),
            (85.0, 11.5, 1.1),
            (90.0, 12.7, 1.2),
            (95.0, 14.0, 1.3),
            (100.0, 15.4, 1.45),
            (105.0, 16.8, 1.6),
            (110.0, 18.4, 1.8),
            (115.0, 20.0, 2.0),
            (120.0, 22.0, 2.2)
        ]
    },
    "Female": {
        "weight_for_age": [
            (0, 3.2, 0.4),
            (3, 5.8, 0.6),
            (6, 7.3, 0.8),
            (9, 8.2, 0.9),
            (12, 8.9, 1.0),
            (18, 10.2, 1.15),
            (24, 11.5, 1.25),
            (30, 12.6, 1.4),
            (36, 13.9, 1.5),
            (42, 15.0, 1.65),
            (48, 15.5, 1.8),
            (54, 16.5, 1.95),
            (60, 17.4, 2.1)
        ],
        "height_for_age": [
            (0, 49.1, 2.0),
            (3, 59.8, 2.2),
            (6, 65.7, 2.5),
            (9, 70.1, 2.6),
            (12, 74.0, 2.7),
            (18, 80.7, 3.0),
            (24, 86.4, 3.2),
            (30, 90.7, 3.4),
            (36, 95.1, 3.6),
            (42, 99.0, 3.8),
            (48, 102.7, 4.0),
            (54, 106.2, 4.2),
            (60, 109.4, 4.4)
        ],
        "weight_for_height": [
            (45.0, 2.4, 0.25),
            (50.0, 3.2, 0.35),
            (55.0, 4.2, 0.45),
            (60.0, 5.4, 0.55),
            (65.0, 6.5, 0.7),
            (70.0, 7.7, 0.8),
            (75.0, 8.9, 0.9),
            (80.0, 9.8, 1.0),
            (85.0, 10.8, 1.1),
            (90.0, 12.0, 1.2),
            (95.0, 13.5, 1.3),
            (100.0, 14.8, 1.45),
            (105.0, 16.4, 1.6),
            (110.0, 18.0, 1.8),
            (115.0, 19.5, 2.0),
            (120.0, 21.5, 2.2)
        ]
    }
}

def interpolate_standard(gender, metric, x_val):
    """Interpolates median and SD for a given x-value (age or height)."""
    dataset = GROWTH_DATA.get(gender, GROWTH_DATA["Male"])[metric]
    x_coords = [item[0] for item in dataset]
    medians = [item[1] for item in dataset]
    sds = [item[2] for item in dataset]
    
    # Clip x_val to the bounds of our data to prevent extrapolation issues
    x_val = max(x_coords[0], min(x_val, x_coords[-1]))
    
    median_val = np.interp(x_val, x_coords, medians)
    sd_val = np.interp(x_val, x_coords, sds)
    return median_val, sd_val

def get_z_score(value, median, sd):
    """Computes basic Z-score."""
    if sd == 0:
        return 0.0
    return (value - median) / sd

def calculate_z_scores(weight_kg, height_cm, age_months, gender):
    """
    Calculates WHO growth standards Z-scores:
    - Weight-for-Age (Underweight)
    - Height-for-Age (Stunting)
    - Weight-for-Height (Wasting)
    """
    # Weight-for-Age
    w_age_med, w_age_sd = interpolate_standard(gender, "weight_for_age", age_months)
    underweight_z = get_z_score(weight_kg, w_age_med, w_age_sd)
    
    # Height-for-Age
    h_age_med, h_age_sd = interpolate_standard(gender, "height_for_age", age_months)
    stunting_z = get_z_score(height_cm, h_age_med, h_age_sd)
    
    # Weight-for-Height
    w_height_med, w_height_sd = interpolate_standard(gender, "weight_for_height", height_cm)
    wasting_z = get_z_score(weight_kg, w_height_med, w_height_sd)
    
    return {
        "underweight_z": float(underweight_z),
        "stunting_z": float(stunting_z),
        "wasting_z": float(wasting_z)
    }

def classify_nutritional_status(z_scores, muac_cm, hemoglobin):
    """
    Returns the severity status and risk score based on WHO criteria and MUAC:
    - Underweight (Weight-for-Age Z < -2)
    - Stunted (Height-for-Age Z < -2)
    - Wasted (Weight-for-Height Z < -2)
    - MUAC < 12.5 cm
    """
    wasting = z_scores["wasting_z"]
    stunting = z_scores["stunting_z"]
    underweight = z_scores["underweight_z"]
    
    min_z = min(wasting, stunting, underweight)
    
    # Determine classification
    status = "Normal"
    risk_score = 0.0
    
    # Base risk score calculations (from Z scores and MUAC)
    # Z-scores mapping to risk: Normal is 0-20, Mild is 20-50, Moderate is 50-80, Severe is 80-100
    if min_z <= -3.0 or muac_cm < 11.5:
        status = "Severe Malnutrition"
        # Map min_z to risk score (e.g. min_z=-3.0 maps to 85, min_z=-4.0 maps to 98)
        risk_score = min(100.0, max(80.0, 80.0 + (abs(min_z) - 3.0) * 10))
    elif min_z <= -2.0 or muac_cm < 12.5:
        status = "Moderate Malnutrition"
        risk_score = min(79.0, max(50.0, 50.0 + (abs(min_z) - 2.0) * 30))
    elif min_z <= -1.0 or muac_cm < 13.5:
        status = "Mild Malnutrition"
        risk_score = min(49.0, max(20.0, 20.0 + (abs(min_z) - 1.0) * 30))
    else:
        status = "Normal"
        # Map min_z above -1.0 to 0-20
        risk_score = max(0.0, min(19.0, (1.0 - min_z) * 10 if min_z < 1.0 else 0.0))
        
    # Anemia risk addition
    if hemoglobin is not None:
        if hemoglobin < 7.0: # Severe Anemia
            risk_score = min(100.0, risk_score + 15.0)
            if status == "Normal":
                status = "Mild Malnutrition"
        elif hemoglobin < 10.0: # Moderate Anemia
            risk_score = min(100.0, risk_score + 10.0)
        elif hemoglobin < 11.0: # Mild Anemia
            risk_score = min(100.0, risk_score + 5.0)
            
    return status, round(risk_score, 1)
