# This script creates 20 new csv files from the simulation data, minicking the process of receiving new claims.
# Run
# /Users/qifenyuan/Skills/AI/fraud-detection-pipeline/.venv/bin/python scripts/generate_new_data.py
# After running this script, you can run the data ingestion script to process these new files.

import pandas as pd
import os
import time
from datetime import datetime

# Configuration
SIMULATION_FILE = 'data/simulation_claims.csv'
OUTPUT_DIR = 'data/raw/new_claims'
CHUNK_SIZE = 10  # Number of claims to generate in each new file
DELAY_SECONDS = 2  # Delay between generating each new file

def generate_new_data():
    """
    Reads the simulation data and generates new claim files in chunks.
    """
    print(f"Reading simulation data from {SIMULATION_FILE}...")
    try:
        simulation_df = pd.read_csv(SIMULATION_FILE)
    except FileNotFoundError:
        print(f"Error: The file {SIMULATION_FILE} was not found.")
        print("Please ensure you have run the data splitting script first.")
        return

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory '{OUTPUT_DIR}' is ready.")

    num_rows = len(simulation_df)
    print(f"Found {num_rows} records in the simulation file.")
    print(f"Generating data in chunks of {CHUNK_SIZE} with a {DELAY_SECONDS}-second delay...\n")

    # Keep track of the original header
    header = simulation_df.columns.tolist()

    for i in range(0, num_rows, CHUNK_SIZE):
        chunk = simulation_df.iloc[i:i + CHUNK_SIZE]
        
        if chunk.empty:
            continue

        # Generate a unique filename with a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'claims_{timestamp}.csv'
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Save the chunk to a new CSV file
        chunk.to_csv(filepath, index=False, header=True)
        
        print(f"Generated: {filename} with {len(chunk)} records.")
        
        # Wait for a few seconds to simulate a real-time feed
        time.sleep(DELAY_SECONDS)

    print("\nData generation complete.")
    print(f"All new claim files have been saved to '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    generate_new_data()
