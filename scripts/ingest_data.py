# This script does the following:
# 1. Watches a Folder: It continuously monitors the new_claims directory for any new CSV files.
# 2. Combines Data: When it finds new files, it reads them all and combines them into a single, larger DataFrame.
# 3. Creates a Batch File: It saves this combined data into a single new CSV file (e.g., claims_batch_20250801_191938.csv) inside the data/source/ directory. This is the directory that dbt will use as its raw data source.
# 4. Moves Processed Files: To avoid processing the same files again, it moves the original small CSVs from new_claims to a processed_claims folder.

import os
import time
import pandas as pd
import shutil
from datetime import datetime

# Configuration
WATCH_DIR = 'data/raw/new_claims'
PROCESSED_DIR = 'data/raw/processed_claims'
DBT_SOURCE_DIR = 'data/source'  # dbt will read from here
POLL_INTERVAL_SECONDS = 5  # How often to check for new files

def ingest_data():
    """
    Watches a directory for new CSV files, combines them, and moves them
    for dbt processing.
    """
    print("Starting data ingestion script...")
    print(f"Watching directory: '{WATCH_DIR}'")
    
    # Ensure required directories exist
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(DBT_SOURCE_DIR, exist_ok=True)
    
    try:
        while True:
            print(f"\nChecking for new files... (Next check in {POLL_INTERVAL_SECONDS}s)")
            
            # Get a list of all CSV files in the watch directory
            files = [f for f in os.listdir(WATCH_DIR) if f.endswith('.csv')]
            
            if not files:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            print(f"Found {len(files)} new claim file(s). Processing...")
            
            all_claims = []
            processed_files = []

            # Read and combine all new files
            for filename in files:
                filepath = os.path.join(WATCH_DIR, filename)
                try:
                    df = pd.read_csv(filepath)
                    all_claims.append(df)
                    processed_files.append(filename)
                    print(f"  - Read {filename}")
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

            if not all_claims:
                print("No valid data to process.")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            # Combine all dataframes into one
            combined_df = pd.concat(all_claims, ignore_index=True)
            
            # Generate a single output file for this batch
            batch_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'claims_batch_{batch_timestamp}.csv'
            output_filepath = os.path.join(DBT_SOURCE_DIR, output_filename)
            
            # Save the combined data to the dbt source directory
            combined_df.to_csv(output_filepath, index=False)
            print(f"\nSuccessfully combined {len(combined_df)} records into '{output_filepath}'")

            # Move the processed files to the 'processed' directory
            for filename in processed_files:
                shutil.move(
                    os.path.join(WATCH_DIR, filename),
                    os.path.join(PROCESSED_DIR, filename)
                )
            print(f"Moved {len(processed_files)} processed files to '{PROCESSED_DIR}'")

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nData ingestion stopped by user.")

if __name__ == "__main__":
    ingest_data()
