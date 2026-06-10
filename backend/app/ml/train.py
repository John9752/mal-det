import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from xgboost import XGBClassifier

# Import WHO standard formulas to help generate realistic synthetic data
from who_standards import interpolate_standard

# Set random seed for reproducibility
np.random.seed(42)

FEATURE_NAMES = [
    "age_months",
    "gender",
    "weight_kg",
    "height_cm",
    "muac_cm",
    "hemoglobin_gdl",
    "dietary_habits",
    "family_income",
    "image_risk_score"
]

def generate_synthetic_data(num_samples=2500):
    """
    Generates a realistic synthetic dataset for training child malnutrition classifiers,
    ensuring profiles correlate with WHO growth benchmarks. Returns (X, y) as numpy arrays.
    """
    X_list = []
    y_list = []
    
    for _ in range(num_samples):
        # 1. Base profile features
        age = np.random.uniform(1.0, 60.0) # 1 to 60 months
        gender = np.random.choice(["Male", "Female"])
        gender_code = 0 if gender == "Male" else 1
        
        income = np.random.choice(["Low", "Medium", "High"], p=[0.4, 0.4, 0.2])
        income_code = 0 if income == "Low" else (1 if income == "Medium" else 2)
        
        diet = np.random.choice(["Poor", "Adequate", "Good"], p=[0.3, 0.4, 0.3])
        diet_code = 0 if diet == "Poor" else (1 if diet == "Adequate" else 2)
        
        # 2. Determine class first to construct realistic physical measurements
        # 0: Normal, 1: Mild, 2: Moderate, 3: Severe
        status_prob = [0.5, 0.25, 0.15, 0.1]
        target_status = np.random.choice([0, 1, 2, 3], p=status_prob)
        
        # Look up WHO medians
        w_med, w_sd = interpolate_standard(gender, "weight_for_age", age)
        h_med, h_sd = interpolate_standard(gender, "height_for_age", age)
        
        # Define physical measurements based on class
        if target_status == 0: # Normal
            # Z-scores between -1 and +1.5
            z_weight = np.random.uniform(-0.8, 1.2)
            z_height = np.random.uniform(-0.8, 1.2)
            muac = np.random.uniform(13.5, 16.5)
            hb = np.random.uniform(11.0, 14.5)
            img_risk = np.random.uniform(0, 25)
        elif target_status == 1: # Mild Malnutrition
            # Z-scores between -2 and -1
            z_weight = np.random.uniform(-1.9, -1.0)
            z_height = np.random.uniform(-1.9, -1.0)
            muac = np.random.uniform(12.5, 13.4)
            hb = np.random.uniform(10.0, 10.9)
            img_risk = np.random.uniform(15, 45)
        elif target_status == 2: # Moderate Malnutrition
            # Z-scores between -3 and -2
            z_weight = np.random.uniform(-2.9, -2.0)
            z_height = np.random.uniform(-2.9, -2.0)
            muac = np.random.uniform(11.5, 12.4)
            hb = np.random.uniform(7.0, 9.9)
            img_risk = np.random.uniform(35, 75)
        else: # Severe Malnutrition
            # Z-scores <= -3
            z_weight = np.random.uniform(-4.5, -3.0)
            z_height = np.random.uniform(-4.5, -3.0)
            muac = np.random.uniform(9.0, 11.4)
            hb = np.random.uniform(4.5, 6.9)
            img_risk = np.random.uniform(60, 100)

        # Convert Z-scores back to weight and height
        weight = w_med + (z_weight * w_sd)
        height = h_med + (z_height * h_sd)
        
        # Keep measurements bounded to physically realistic limits
        weight = max(1.5, weight)
        height = max(40.0, height)
        muac = max(7.0, muac)
        hb = max(3.0, hb)
        
        # Features index order matches prediction feature array
        X_list.append([
            age, 
            gender_code, 
            weight, 
            height, 
            muac, 
            hb, 
            diet_code, 
            income_code, 
            img_risk
        ])
        y_list.append(target_status)
        
    return np.array(X_list), np.array(y_list)

def oversample_classes(X, y):
    """Simple random oversampling to balance minority classes (MAM/SAM)."""
    classes, counts = np.unique(y, return_counts=True)
    max_count = max(counts)
    
    X_resampled = []
    y_resampled = []
    
    for c in classes:
        indices = np.where(y == c)[0]
        resampled_indices = np.random.choice(indices, size=max_count, replace=True)
        X_resampled.append(X[resampled_indices])
        y_resampled.append(y[resampled_indices])
        
    return np.vstack(X_resampled), np.concatenate(y_resampled)

def train_and_evaluate():
    print("Generating synthetic child growth dataset...")
    X, y = generate_synthetic_data(2500)
    
    # Split train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Oversample minority classes to balance dataset for model training
    X_train_resampled, y_train_resampled = oversample_classes(X_train, y_train)
    
    # Scale features using the balanced training set
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)
    y_train = y_train_resampled
    
    # Initialize models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, eval_metric='mlogloss'),
        "Neural Network (MLP)": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
    }
    
    results = {}
    best_acc = 0
    best_model_name = ""
    best_model_obj = None
    
    # Train and evaluate each model
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='weighted')
        
        results[name] = {
            "Accuracy": acc,
            "Precision": precision,
            "Recall": recall,
            "F1 Score": f1
        }
        
        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_model_obj = model
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_acc:.4f}")
    
    # Save best model and scaler
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    model_path = os.path.join(os.path.dirname(__file__), "best_model.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(best_model_obj, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
        
    print(f"Saved model and scaler to {os.path.dirname(__file__)}")
    
    # Compute and plot Feature Importance (using Random Forest)
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title("Malnutrition Classification - Feature Importance (Random Forest)")
    plt.bar(range(X.shape[1]), importances[indices], align="center", color="#4f46e5")
    plt.xticks(range(X.shape[1]), [FEATURE_NAMES[i] for i in indices], rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the feature importance chart
    importance_img_path = os.path.join(os.path.dirname(__file__), "feature_importance.png")
    plt.savefig(importance_img_path)
    plt.close()
    print(f"Saved feature importance plot to {importance_img_path}")
    
    # Generate model performance report in Markdown
    report_content = f"""# Malnutrition Detection AI Model Training Report

An evaluation of machine learning models trained on child growth measurements alongside computer vision features to classify malnutrition severity levels: **Normal**, **Mild Malnutrition**, **Moderate Malnutrition**, and **Severe Malnutrition**.

## Evaluation Results

| Model Name | Accuracy | Precision | Recall | F1 Score |
| :--- | :---: | :---: | :---: | :---: |
"""
    for name, metrics in results.items():
        report_content += f"| {name} | {metrics['Accuracy']:.4f} | {metrics['Precision']:.4f} | {metrics['Recall']:.4f} | {metrics['F1 Score']:.4f} |\n"
        
    report_content += f"""
### Selected Classifier
- **Model Type**: {best_model_name}
- **Accuracy**: {best_acc:.2%}

## Feature Importance Analysis

The relative importance of physical and demographic inputs in predicting child malnutrition is shown below (derived from the Random Forest model):

"""
    # List feature importance rankings
    for rank, idx in enumerate(indices):
        report_content += f"{rank+1}. **{FEATURE_NAMES[idx]}**: {importances[idx]:.2%}\n"
        
    report_path = os.path.join(os.path.dirname(__file__), "model_report.md")
    with open(report_path, "w") as f:
        f.write(report_content)
        
    print(f"Model report written to {report_path}")

if __name__ == "__main__":
    train_and_evaluate()
