# Making predictions on new data (suggested by Claude Sonnet 4).
# But I have not yet tested this code!

import joblib
import pandas as pd
import numpy as np
import json
from datetime import datetime

class FraudPredictor:
    def __init__(self, model_path='models/ada_boost_fraud_model.pkl', 
                 scaler_path='models/feature_scaler.pkl'):
        """Load the trained model and scaler"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        # Load metadata
        with open('models/model_metadata.json', 'r') as f:
            self.metadata = json.load(f)
        
        print(f"✅ Model loaded - trained on {self.metadata['training_date']}")
        print(f"📊 Model performance - Fraud F1: {self.metadata['fraud_f1_score']}")
    
    def preprocess_data(self, raw_data):
        """Preprocess new data the same way as training data"""
        df = raw_data.copy()
        
        # Handle missing values (same as training)
        df.replace('?', np.nan, inplace=True)
        
        # Fill missing values with mode (you might want to save these values from training)
        categorical_columns = ['collision_type', 'authorities_contacted', 
                             'property_damage', 'police_report_available']
        
        for col in categorical_columns:
            if col in df.columns and df[col].isna().any():
                mode_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                df[col] = df[col].fillna(mode_value)
        
        # Drop the same columns as in training
        columns_to_drop = ['policy_number','policy_bind_date','policy_state',
                          'insured_zip','incident_location','incident_date',
                          'incident_state','incident_city','insured_hobbies',
                          'auto_make','auto_model','auto_year', '_c39',
                          'age', 'total_claim_amount']
        
        # Only drop columns that exist
        columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        df.drop(columns=columns_to_drop, inplace=True)
        
        # Remove target column if present
        if 'fraud_reported' in df.columns:
            df.drop(columns=['fraud_reported'], inplace=True)
        
        # One-hot encode categorical features
        categorical_features = df.select_dtypes(include=['object'])
        if len(categorical_features.columns) > 0:
            categorical_encoded = pd.get_dummies(categorical_features, drop_first=True)
            numerical_features = df.select_dtypes(include=['float64', 'int64'])
            df = pd.concat([numerical_features, categorical_encoded], axis=1)
        
        # Scale numerical features
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numerical_cols) > 0:
            df[numerical_cols] = self.scaler.transform(df[numerical_cols])
        
        return df
    
    def predict(self, raw_data):
        """Make fraud predictions on new data"""
        # Preprocess the data
        processed_data = self.preprocess_data(raw_data)
        
        # Make predictions
        predictions = self.model.predict(processed_data)
        probabilities = self.model.predict_proba(processed_data)
        
        # Create results dataframe
        results = pd.DataFrame({
            'fraud_prediction': predictions,
            'fraud_probability': probabilities[:, 1],  # Probability of fraud class
            'prediction_date': datetime.now().isoformat()
        })
        
        return results
    
    def predict_single(self, claim_data):
        """Predict fraud for a single claim (dictionary input)"""
        df = pd.DataFrame([claim_data])
        result = self.predict(df)
        return {
            'is_fraud': bool(result['fraud_prediction'].iloc[0]),
            'fraud_probability': float(result['fraud_probability'].iloc[0]),
            'confidence': 'High' if result['fraud_probability'].iloc[0] > 0.8 else 
                         'Medium' if result['fraud_probability'].iloc[0] > 0.5 else 'Low'
        }

# Example usage
if __name__ == "__main__":
    # Load the predictor
    predictor = FraudPredictor()
    
    # Example: predict on new data
    # new_data = pd.read_csv('data/new_claims.csv')
    # predictions = predictor.predict(new_data)
    # print(predictions)
    
    # Example: single prediction
    sample_claim = {
        'months_as_customer': 24,
        'policy_annual_premium': 1500,
        'umbrella_limit': 0,
        'incident_severity': 'Minor Damage',
        'authorities_contacted': 'Police',
        'incident_type': 'Single Vehicle Collision',
        # ... add more features as needed
    }
    
    result = predictor.predict_single(sample_claim)
    print(f"Fraud prediction: {result}")