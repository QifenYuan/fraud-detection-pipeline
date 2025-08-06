# The Re-imagined "Fraud Detection Pipeline"

This document outlines the vision for an integrated, end-to-end pipeline for detecting fraudulent insurance claims.

Think of the project as a machine that takes in raw insurance claims and outputs fraud predictions. Here’s the assembly line:

1.  **Data Ingestion**: A script automatically picks up new claim files. [done!]
2.  **Data Transformation**: dbt select and cast all 40 columns of raw data. [done!]
3.  **Model Training**: A script loads data from dbt, and train an self-contained prediction model pipeline. [done!] [next-identical_prediction/model_insensitive]
4.  **Prediction Service**: An API serves the latest model, ready to make predictions on new, individual claims. [done!]

Here is a diagram illustrating this flow:

```mermaid
graph TD
    A[Raw Data<br>(data/raw/new_claims/*.csv)] -->|1. Ingestion Script<br>(scripts/ingest_data.py)| B(Source Data<br>(data/source/*.csv))
    B -->|2. dbt run| C{dbt Models<br>(dbt_project/)}
    C -->|staging| D[Staging Table<br>(stg_claims)]
    D -->|marts| E[Fact Table<br>(fct_claims_predictions)]
    E -->|3. Training Script<br>(dbt_model_training.ipynb)| F(ML Model<br>(models/dbt_fraud_detection_pipeline.pkl))
    F -->|4. API<br>(app/main.py)| G{Prediction Endpoint<br>(/predict)}
    H[User Request<br>(JSON)] --> G
    G --> I[Prediction Response<br>(JSON)]

    subgraph "Data Transformation (dbt)"
        C
        D
        E
    end

    subgraph "Model Serving (FastAPI)"
        F
        G
        H
        I
    end
```

### How We'll Connect The Existing Work

Based on this vision, here are the connections we need to make:

1.  **Connect Data Ingestion to dbt**:
    *   Your `scripts/ingest_data.py` is already set up to move data. We need to ensure your dbt project's `sources.yml` is configured to read from the `data/source` directory that your script uses.

2.  **Connect dbt to Model Training**:
    *   Your `train_model.ipynb` currently reads from a static CSV (`data/insurance_claims.csv`). We will modify it to be a Python script (`scripts/train_model.py`) that reads the clean, transformed data directly from the dbt-created table (`fct_claims_predictions`) in your DuckDB database. This ensures your model is always trained on the latest, highest-quality data.

3.  **Orchestrate the Pipeline**:
    *   We can create a simple shell script (e.g., `run_pipeline.sh`) or a Python script that executes these steps in order:
        1.  Run the ingestion script.
        2.  Run `dbt run`.
        3.  Run the model training script.
        4.  Start the FastAPI server.

This approach turns your collection of scripts and models into a true, end-to-end pipeline. It's a much more powerful story to tell and a more robust system.
