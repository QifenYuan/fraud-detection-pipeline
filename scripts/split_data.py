# This script splits the raw insurance claims data into training and simulation datasets.
# The training data is used for machine learning model training.
# The simulation data is used to minic receiving new claims.

import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Define file paths
raw_data_path = os.path.join("data", "insurance_claims.csv") # raw data 
train_data_path = os.path.join("data", "train_claims.csv") # data used for training ML models
simulation_data_path = os.path.join("data", "simulation_claims.csv") # data used for simulation

# Load the dataset
print(f"Loading data from {raw_data_path}...")
df = pd.read_csv(raw_data_path)

# Split the data
print("Splitting data into training and simulation sets (80/20)...")
train_df, simulation_df = train_test_split(df, test_size=0.2, random_state=42)

# Save the split datasets
print(f"Saving training data to {train_data_path}...")
train_df.to_csv(train_data_path, index=False)

print(f"Saving simulation data to {simulation_data_path}...")
simulation_df.to_csv(simulation_data_path, index=False)

print("Data splitting complete.")
