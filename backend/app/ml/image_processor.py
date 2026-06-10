import cv2
import numpy as np
import os

# Get path of built-in OpenCV Haar Cascade for face detection
HAAR_CASCADE_PATH = os.path.join(
    os.path.dirname(cv2.__file__), 
    'data', 
    'haarcascade_frontalface_default.xml'
)

def analyze_child_image(image_path: str):
    """
    Analyzes an uploaded child photograph to extract CV features related to malnutrition:
    - Face detection (facial presence)
    - Face aspect ratio (wasting/hollowness indicator)
    - Skin color distribution (pallor / anemia indicator)
    - Cheek shadow variance (hollow cheeks indicator)
    """
    results = {
        "face_detected": False,
        "aspect_ratio": 0.0,
        "skin_pallor_index": 0.0,
        "cheek_shadow_index": 0.0,
        "image_risk_score": 0.0,
        "message": "No image processed"
    }

    if not image_path or not os.path.exists(image_path):
        results["message"] = "Image path does not exist"
        return results

    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            results["message"] = "Unable to read image"
            return results

        h, w, c = img.shape

        # 1. CLAHE Brightness & Contrast Normalization (enhances shadow/color details invariant to lighting)
        lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab_img)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_chan)
        limg = cv2.merge((cl, a_chan, b_chan))
        img_equalized = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        gray = cv2.cvtColor(img_equalized, cv2.COLOR_BGR2GRAY)

        # Load cascade classifier
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        if face_cascade.empty():
            # Fallback if cascade not found in CV2 folder
            if os.path.exists("haarcascade_frontalface_default.xml"):
                face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            else:
                results["message"] = "Haar cascade classifier file not found"
                return results

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))

        # 2. Extract ROI & Aspect Ratio with fallback to center region
        if len(faces) == 0:
            results["message"] = "No face detected; analyzed center region"
            # Fallback to center 40% of the image assuming centered framing
            fx, fy, fw, fh = int(w * 0.3), int(h * 0.3), int(w * 0.4), int(h * 0.4)
            face_roi = img_equalized[fy:fy+fh, fx:fx+fw]
            face_roi_gray = gray[fy:fy+fh, fx:fx+fw]
            aspect_ratio = 0.85 # Normal ratio reference
        else:
            results["face_detected"] = True
            results["message"] = "Image analyzed successfully"
            # Use largest detected face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            fx, fy, fw, fh = faces[0]
            aspect_ratio = float(fw) / float(fh)
            face_roi = img_equalized[fy:fy+fh, fx:fx+fw]
            face_roi_gray = gray[fy:fy+fh, fx:fx+fw]

        results["aspect_ratio"] = round(aspect_ratio, 3)

        # 3. LAB Color Space Skin Pallor Index (Anemia / Pale skin check)
        # In LAB space, higher 'a' indicates more red. Pale skin has a lower 'a' value.
        roi_lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
        avg_a = np.mean(roi_lab[:, :, 1]) # Index 1 is the 'a' channel
        
        # Calculate skin pallor: lower relative red saturation in skin (base average value is ~148)
        # We index it such that higher values mean higher pallor (risk)
        pallor_index = 155.0 / max(100.0, avg_a)
        results["skin_pallor_index"] = round(float(pallor_index), 3)

        # 4. Cheek Shadow Index (Hollow cheeks / muscle wasting indicator)
        # Analyze lower cheek regions relative to face dimensions
        cy1, cy2 = int(0.55 * fh), int(0.8 * fh)
        clx1, clx2 = int(0.15 * fw), int(0.4 * fw)
        crx1, crx2 = int(0.6 * fw), int(0.85 * fw)

        left_cheek = face_roi_gray[cy1:cy2, clx1:clx2]
        right_cheek = face_roi_gray[cy1:cy2, crx1:crx2]

        cheek_variance = 0.0
        if left_cheek.size > 0 and right_cheek.size > 0:
            left_std = np.std(left_cheek)
            right_std = np.std(right_cheek)
            cheek_variance = (left_std + right_std) / 2.0
            
        cheek_shadow_index = min(10.0, cheek_variance / 5.0)
        results["cheek_shadow_index"] = round(float(cheek_shadow_index), 3)

        # 5. Combined Image Risk Score
        cv_risk = 0.0
        if pallor_index > 1.05: # Index above 1.05 means potential anemia/pallor
            cv_risk += (pallor_index - 1.05) * 150.0
        if cheek_shadow_index > 5.0: # Variance above 5 indicates hollow cheeks
            cv_risk += (cheek_shadow_index - 5.0) * 8.0
        if aspect_ratio < 0.8: # Narrow face shape
            cv_risk += (0.8 - aspect_ratio) * 100.0
            
        results["image_risk_score"] = round(min(100.0, max(0.0, cv_risk)), 1)

    except Exception as e:
        results["message"] = f"Error processing image: {str(e)}"

    return results
