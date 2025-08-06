from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import os
from typing import Literal
from contextlib import asynccontextmanager

# --- Configuration ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'dbt_fraud_detection_pipeline.pkl')

# --- Global Artifacts ---
model = None

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI app. It will run the startup code before yielding
    and the shutdown code after.
    """
    # Startup: Load the model
    global model
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model pipeline loaded successfully.")
    except FileNotFoundError:
        print(f"❌ Model file not found at {MODEL_PATH}")
        model = None
    except Exception as e:
        print(f"❌ An unexpected error occurred during model loading: {e}")
        model = None
    
    yield
    
    # Shutdown: Clean up the resources
    print("🧹 Cleaning up and shutting down.")
    model = None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Insurance Fraud Detection API",
    description="An API to predict fraudulent insurance claims using a scikit-learn pipeline.",
    version="2.0.0",
    lifespan=lifespan
)

# --- Pydantic Models for Input Validation ---
# This model represents all the raw features required by the pipeline
class Claim(BaseModel):
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
    capital_gains: int
    capital_loss: int
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
    # _c39 is excluded as it's always null

class PredictionResponse(BaseModel):
    prediction: Literal['Y', 'N']
    probability: float

# --- API Endpoints ---
@app.get("/", tags=["Status"])
def read_root():
    """
    Root endpoint to check API status.
    """
    return {"status": "API is running"}

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_fraud(claim: Claim):
    """
    Predict fraud for a single insurance claim.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check server logs.")

    try:
        # Convert the Pydantic model to a dictionary
        input_data = claim.model_dump()

        # Convert to DataFrame
        df = pd.DataFrame([input_data])

        # --- Feature Engineering (Replicating dbt model) ---

        # 1. Date-based features (This was in the original notebook)
        df['policy_bind_date'] = pd.to_datetime(df['policy_bind_date'])
        # For prediction, we'll use today's date as the reference for policy age
        df['policy_age_days'] = (pd.to_datetime('today') - df['policy_bind_date']).dt.days

        # 2. One-Hot Encoding for categorical variables
        # The model was trained on these specific columns. We create them here and set them
        # based on the input data.
        
        # policy_csl
        df['policy_csl_100_300'] = (df['policy_csl'] == '100/300').astype(int)
        df['policy_csl_250_500'] = (df['policy_csl'] == '250/500').astype(int)
        df['policy_csl_500_1000'] = (df['policy_csl'] == '500/1000').astype(int)

        # insured_education_level
        education_levels = ['Associate', 'College', 'High School', 'JD', 'MD', 'Masters', 'PhD']
        for level in education_levels:
            df[f'insured_education_level_{level}'] = (df['insured_education_level'] == level).astype(int)

        # insured_relationship
        relationships = ['not-in-family', 'other-relative', 'own-child', 'unmarried', 'wife', 'husband']
        for rel in relationships:
            df[f'insured_relationship_{rel}'] = (df['insured_relationship'] == rel).astype(int)

        # incident_type
        incident_types = ['Multi-vehicle Collision', 'Parked Car', 'Single Vehicle Collision', 'Vehicle Theft']
        for itype in incident_types:
            df[f'incident_type_{itype.replace(" ", "_")}'] = (df['incident_type'] == itype).astype(int)

        # collision_type
        collision_types = ['Front Collision', 'Rear Collision', 'Side Collision']
        for ctype in collision_types:
            df[f'collision_type_{ctype.replace(" ", "_")}'] = (df['collision_type'] == ctype).astype(int)

        # incident_severity
        severities = ['Major Damage', 'Minor Damage', 'Total Loss', 'Trivial Damage']
        for sev in severities:
            df[f'incident_severity_{sev.replace(" ", "_")}'] = (df['incident_severity'] == sev).astype(int)

        # authorities_contacted
        authorities = ['Ambulance', 'Fire', 'None', 'Other', 'Police']
        for auth in authorities:
            df[f'authorities_contacted_{auth}'] = (df['authorities_contacted'] == auth).astype(int)

        # Binary features
        df['property_damage_YES'] = (df['property_damage'] == 'YES').astype(int)
        df['police_report_available_YES'] = (df['police_report_available'] == 'YES').astype(int)
        df['insured_sex_MALE'] = (df['insured_sex'] == 'MALE').astype(int)

        # 3. Select and order columns to match model's expectation
        # This is CRITICAL. The order must be exactly the same as during training.
        model_features = model.feature_names_in_
        df_final = df[model_features]

        # The pipeline handles all preprocessing. We just predict.
        prediction = model.predict(df_final)
        probability = model.predict_proba(df_final)

        # Get the probability of the predicted class
        predicted_label = prediction[0]
        class_index = list(model.classes_).index(predicted_label)
        prediction_probability = float(probability[0, class_index])

        return PredictionResponse(
            prediction=predicted_label, 
            probability=prediction_probability
        )
    except Exception as e:
        # Log the error for debugging
        print(f"❌ Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during prediction.")