# Malnutrition Detection AI Model Training Report

An evaluation of machine learning models trained on child growth measurements alongside computer vision features to classify malnutrition severity levels: **Normal**, **Mild Malnutrition**, **Moderate Malnutrition**, and **Severe Malnutrition**.

## Evaluation Results

| Model Name | Accuracy | Precision | Recall | F1 Score |
| :--- | :---: | :---: | :---: | :---: |
| Logistic Regression | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Random Forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| XGBoost | 0.9980 | 0.9980 | 0.9980 | 0.9980 |
| Neural Network (MLP) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Selected Classifier
- **Model Type**: Logistic Regression
- **Accuracy**: 100.00%

## Feature Importance Analysis

The relative importance of physical and demographic inputs in predicting child malnutrition is shown below (derived from the Random Forest model):

1. **muac_cm**: 43.21%
2. **hemoglobin_gdl**: 34.71%
3. **image_risk_score**: 16.22%
4. **weight_kg**: 4.26%
5. **height_cm**: 0.97%
6. **age_months**: 0.63%
7. **family_income**: 0.01%
8. **dietary_habits**: 0.00%
9. **gender**: 0.00%
