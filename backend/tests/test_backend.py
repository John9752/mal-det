import os
import sys
import numpy as np
import cv2

# Set python path to find app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.who_standards import calculate_z_scores, classify_nutritional_status
from app.ml.image_processor import analyze_child_image
from app.ml.recommendations import get_nutrition_recommendations, get_scheme_recommendations

def test_who_standards():
    print("--- Testing WHO Z-Score calculations ---")
    # Test Normal Male Child 12 months, weight 9.6, height 75.7 (WHO medians)
    z_scores = calculate_z_scores(weight_kg=9.6, height_cm=75.7, age_months=12.0, gender="Male")
    print(f"Normal: {z_scores}")
    assert abs(z_scores["underweight_z"]) < 0.1
    assert abs(z_scores["stunting_z"]) < 0.1
    assert abs(z_scores["wasting_z"]) < 0.1
    
    status, risk = classify_nutritional_status(z_scores, muac_cm=14.0, hemoglobin=12.0)
    print(f"Normal Status: {status}, Risk: {risk}")
    assert status == "Normal"

    # Test Severe Malnourished Child (very low weight/height)
    z_scores_severe = calculate_z_scores(weight_kg=5.0, height_cm=62.0, age_months=12.0, gender="Male")
    print(f"Severe: {z_scores_severe}")
    assert z_scores_severe["underweight_z"] < -3.0
    assert round(z_scores_severe["wasting_z"], 2) <= -2.0
    
    status_severe, risk_severe = classify_nutritional_status(z_scores_severe, muac_cm=10.0, hemoglobin=6.0)
    print(f"Severe Status: {status_severe}, Risk: {risk_severe}")
    assert status_severe == "Severe Malnutrition"
    assert risk_severe >= 80.0
    print("WHO Standards Test PASSED.")

def test_recommendations():
    print("\n--- Testing Recommendations ---")
    nutrition = get_nutrition_recommendations(status="Severe Malnutrition", age_months=12.0, weight_kg=5.0, state="Telangana")
    print(f"Nutrition: {nutrition['required_calories']} Kcal, {nutrition['required_protein_g']}g protein. Region: {nutrition['region']}")
    assert nutrition["required_calories"] > 500
    assert nutrition["region"] == "South India"

    schemes = get_scheme_recommendations(age_months=12.0, gender="Female", status="Severe Malnutrition", income="Low", state="Telangana")
    print(f"Schemes count: {len(schemes)}")
    for s in schemes:
        print(f" - {s['name']}")
    assert len(schemes) >= 3
    print("Recommendations Test PASSED.")

def test_image_processor():
    print("\n--- Testing Image Processor (OpenCV) ---")
    # Generate a dummy image (e.g. gray face profile) to test CV pipeline handling
    dummy_img_path = "test_dummy.png"
    dummy_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    cv2.imwrite(dummy_img_path, dummy_img)
    
    try:
        results = analyze_child_image(dummy_img_path)
        print(f"CV Results on dummy image: {results}")
        # Face detection should be False for a blank canvas, but it should exit gracefully
        assert results["face_detected"] is False
        print("Image Processor Test PASSED.")
    finally:
        if os.path.exists(dummy_img_path):
            os.remove(dummy_img_path)

def test_pdf_report():
    print("\n--- Testing PDF Report Generation ---")
    class MockChild:
        def __init__(self):
            self.name = "Aarav Kumar"
            self.gender = "Male"
            self.age_months = 18.0
            self.family_income = "Low"
            self.village = "Malkajgiri"
            self.district = "Medchal-Malkajgiri"
            self.state = "Telangana"
            self.parent_name = "Ramesh Kumar"
            from datetime import datetime
            self.created_at = datetime.utcnow()
            
    class MockRecord:
        def __init__(self):
            self.weight_kg = 8.5
            self.height_cm = 74.5
            self.muac_cm = 11.2
            self.hemoglobin_gdl = 9.5
            self.wasting_z = -2.8
            self.stunting_z = -1.9
            self.underweight_z = -2.5
            self.status = "Moderate Malnutrition"
            self.risk_score = 64.0
            from datetime import datetime
            self.recorded_at = datetime.utcnow()
            
    child = MockChild()
    record = MockRecord()
    
    from app.ml.recommendations import get_nutrition_recommendations, get_scheme_recommendations
    nutrition = get_nutrition_recommendations(record.status, child.age_months, record.weight_kg, child.state)
    schemes = get_scheme_recommendations(child.age_months, child.gender, record.status, child.family_income, child.state)
    
    from app.reports import generate_child_health_card_pdf
    pdf_buffer = generate_child_health_card_pdf(child, record, nutrition, schemes)
    pdf_bytes = pdf_buffer.read()
    
    print(f"Generated PDF size: {len(pdf_bytes)} bytes")
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
    print("PDF Report Test PASSED.")

def test_voice_assistant():
    print("\n--- Testing Voice Assistant ---")
    from app.main import transcribe_voice
    import asyncio
    
    class MockFile:
        async def read(self):
            return b"dummy audio content"
            
    mock_audio = MockFile()
    result = asyncio.run(transcribe_voice(audio=mock_audio, language="te"))
    
    print(f"Voice Assistant Result (Telugu): status={result['status']}, lang={result['language_detected']}, slots={result['slots_extracted']}")
    assert result["status"] == "success"
    assert result["language_detected"] == "te"
    assert result["slots_extracted"]["weight_kg"] == 9.0
    print("Voice Assistant Test PASSED.")

if __name__ == "__main__":
    test_who_standards()
    test_recommendations()
    test_image_processor()
    test_pdf_report()
    test_voice_assistant()
    print("\nALL BACKEND CORE TESTS PASSED.")
