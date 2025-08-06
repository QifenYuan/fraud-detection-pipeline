import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

# Define the list of columns to drop
# We define this here so it can be used in our custom transformer
columns_to_drop = [
    'policy_bind_date', 'incident_date', 'policy_number', 'policy_state',
    'insured_zip', 'insured_hobbies', 'incident_location', 'incident_city',
    'incident_state', 'auto_model', 'auto_year', 'auto_make', '_c39'
]

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_transformed = X.copy()
        
        # Standardize column names
        X_transformed.columns = [col.lower().replace('-', '_') for col in X_transformed.columns]
        
        # Replace '?' with NaN
        X_transformed.replace('?', np.nan, inplace=True)
        
        # Feature Engineering: policy_age_days
        X_transformed['policy_bind_date'] = pd.to_datetime(X_transformed['policy_bind_date'])
        X_transformed['incident_date'] = pd.to_datetime(X_transformed['incident_date'])
        X_transformed['policy_age_days'] = (X_transformed['incident_date'] - X_transformed['policy_bind_date']).dt.days
        
        # Drop specified columns
        # We use .get(columns_to_drop, []) to avoid errors if columns are already gone
        cols_to_drop_in_df = [col for col in columns_to_drop if col in X_transformed.columns]
        X_transformed.drop(columns=cols_to_drop_in_df, inplace=True)
        
        return X_transformed
