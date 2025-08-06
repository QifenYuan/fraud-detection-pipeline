from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os
from app.feature_engineer import FeatureEngineer
import logging

# Path to the trained model pipeline
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'dbt_fraud_detection_pipeline.pkl')

# Load the model at startup
app = FastAPI(title="Fraud Detection API")
model = joblib.load(MODEL_PATH)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the input schema (all raw features)
class Claim(BaseModel):
    """Input schema for insurance claim prediction."""
    months_as_customer: int
    age: int
    policy_number: int
    policy_bind_date: str
    policy_state: str
    policy_csl: str
    policy_deductable: int
    policy_annual_premium: float
    umbrella_limit: int
    insured_zip: int
    insured_sex: str
    insured_education_level: str
    insured_occupation: str
    insured_hobbies: str
    insured_relationship: str
    capital_gains: int = Field(..., alias="capital-gains")
    capital_loss: int = Field(..., alias="capital-loss")
    incident_date: str
    incident_type: str
    collision_type: str
    incident_severity: str
    authorities_contacted: str
    incident_state: str
    incident_city: str
    incident_location: str
    incident_hour_of_the_day: int
    number_of_vehicles_involved: int
    property_damage: str
    bodily_injuries: int
    witnesses: int
    police_report_available: str
    total_claim_amount: int
    injury_claim: int
    property_claim: int
    vehicle_claim: int
    auto_make: str
    auto_model: str
    auto_year: int
    
    class Config:
        validate_by_name = True

class PredictionResponse(BaseModel):
    prediction: str
    probability: float

@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(claim: Claim) -> PredictionResponse:
    """Predict whether an insurance claim is fraudulent based on input features."""
    try:
        # Convert input to DataFrame
        df = pd.DataFrame([claim.model_dump()])
        logging.info(f"Received input: {df.to_dict(orient='records')[0]}")

        # The pipeline has a FeatureEngineer step, extract and apply it for logging
        fe_step = None
        if hasattr(model, 'named_steps') and 'featureengineer' in model.named_steps:
            fe_step = model.named_steps['featureengineer']
        if fe_step is not None:
            transformed = fe_step.transform(df.copy())
            logging.info(f"After FeatureEngineer: {transformed.iloc[0].to_dict()}")
        else:
            logging.info("No FeatureEngineer step found in pipeline.")

        # The pipeline handles all preprocessing
        pred = model.predict(df)[0]
        prob = float(model.predict_proba(df)[0][list(model.classes_).index(pred)])
        label_map = {"0": "Not a fraud", "1": "Fraud"}
        label = label_map.get(str(pred), str(pred))
        logging.info(f"Prediction: {label}, Probability: {prob}")
        return PredictionResponse(prediction=label, probability=prob)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")