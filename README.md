# Predictive Fraud Detection Pipeline for Auto Insurance

A robust, end-to-end MLOps pipeline for auto insurance fraud detection, featuring automated data ingestion, dbt-powered transformation, scikit-learn modeling, and FastAPI serving.

---


## Project Overview

- **Automated Data Ingestion:** Continuously watches for new raw claim CSVs, batches and moves them for dbt processing (see `scripts/ingest_data.py`).
- **Data Transformation:** Cleans and type-casts raw data using dbt (DuckDB backend).
- **Model Training:** Builds a reproducible scikit-learn pipeline, including custom feature engineering (see `dbt_model_training.ipynb`).
- **Model Serving:** Deploys the trained model as a production-ready REST API with FastAPI.
- **Testing:** Provides sample JSONs and instructions for API testing.

---


## Architecture

```
Raw Data
   |
   v
Automated Ingestion Script (ingest_data.py)
   |
   v
dbt: stg_claims.sql
   |
   v
dbt: fct_claims_predictions.sql
   |
   v
Model Training (sklearn Pipeline)
   |
   v
Trained Model (.pkl)
   |
   v
FastAPI Prediction Service
   |
   v
API Client (curl/Postman)
```

---

## Tech Stack

- **Python (pandas, os, shutil, time):** Automated data ingestion and file management
- **dbt (DuckDB):** Data transformation and cleaning
- **scikit-learn:** Feature engineering and model training
- **FastAPI & Pydantic:** Model serving as a REST API and input validation
- **joblib:** Model serialization
- **Docker:** (Optional) Containerization

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fraud-detection-pipeline.git
cd fraud-detection-pipeline
```

### 2. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Ingest Data

Add new claim CSV files to `data/raw/new_claims/`.  
Run the data ingestion script in a separate terminal to monitor for new files, batch them, and move them for dbt processing:

```bash
python scripts/ingest_data.py
```


### 4. Run dbt Models

```bash
cd dbt_project
dbt run
cd ..
```

### 5. Train the Model

Open and run all cells in `dbt_model_training.ipynb` to train and save the model pipeline.

### 6. Start the API Server

```bash
uvicorn app.main:app --reload
```

### 7. Test the API

Use Postman or curl to send POST requests to `http://127.0.0.1:8000/predict` with sample JSONs from `data/test_samples/`.

---

## Example API Request

Send a sample insurance claim to the prediction endpoint using curl:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d @data/test_samples/sample_1.json
```

---


## Project Highlights

- **Automated data ingestion:** Continuously processes new claim files for seamless integration.
- **Reproducible pipeline:** All steps, from data to deployment, are versioned and automated.
- **Custom feature engineering:** Easily extendable for new features.
- **Production-ready API:** FastAPI with Pydantic validation.
- **Test samples included:** For easy demonstration and validation.

---

## Next Steps

- Improve model sensitivity (see `model_sensitivity_analysis.ipynb`)
- Add Docker support for full containerization
- Integrate CI/CD for automated testing and deployment
- (Optional) Add monitoring, logging, and data drift detection
- Contributions welcome! Feel free to open issues or pull requests for new features.

---


## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

Qifen (Susie) Yuan
qifenyuan@gmail.com  
[LinkedIn](https://www.linkedin.com/in/qifen-susie-yuan-a888b58a/)  
[GitHub](https://github.com/QifenYuan)