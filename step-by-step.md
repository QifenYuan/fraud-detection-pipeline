## Initial Plan - Building an End-to-End Insurance Claim Prediction Pipeline

**The goal** is to build a model to predict fraudulent insurance claims, and engineer the system around it, demonstrating my skills in data integration, data flow, Python, SQL, dbt, ML modeling, and MLOps concepts. 

Project Title: "Predictive Fraud Detection Pipeline for Auto Insurance"

1. **Formalize the Data Pipeline Steps**

Defining how they connect to form a cohesive pipeline.

- **Data Ingestion**: Create a dedicated Python script in `scripts/ingest_data.py`. This script can watch a directory (e.g., `data/raw/new_claims`) for incoming CSV files and move them to a `data/source` directory that **dbt** will use. This simulates a more realistic data ingestion flow.

- **Data Transformation (dbt)**: This is a critical piece to showcase. I recommend structuring your dbt models to reflect best practices:
  - `dbt_project/models/staging/`: Clean and prepare your raw data here. For example, stg_claims.sql would select from your source data, cast data types, and rename columns
  - `dbt_project/models/marts/`: Create your final, clean data models here. For instance, fct_claims_predictions.sql would contain the feature-engineered data ready for the ML model.

- **Model Training**: Your notebook is great for exploration. Consider creating a scripts/train_model.py that reads the clean data from your dbt "mart" table to train and save the model. This makes the training process repeatable and scriptable.

2. **Enhance the Model Serving API**

For your FastAPI application, think about what a real-world prediction service would need.

- **Input Validation**: Use Pydantic models in your FastAPI app (`app/main.py`) to define and validate the structure of incoming prediction requests. This ensures data quality and provides clear error messages for bad requests.

- **Prediction Endpoint**: Your `/predict` endpoint should accept a single claim's data as JSON, load `models/fraud_detection_pipeline.pkl`, and return a clear JSON response, like {"prediction": "fraud"} or {"prediction": "not_fraud", "probability": 0.85}.

2. **Add Testing and Validation**
To make your project more professional, add automated testing:

- **dbt Tests**: Use dbt's built-in testing to assert data quality in your models (e.g., not_null, unique).
- **API Tests**: Use pytest to write tests for your FastAPI endpoints to ensure they behave as expected.

4. **Improve Configuration Management**
Avoid hardcoding values like file paths or model names. Use a configuration file (e.g., `config.yaml`) or environment variables to manage these settings. This makes your project easier to configure and run in different environments.

These suggestions can help you build a more integrated and production-ready pipeline. You're on the right track, and I'm here to help if you want to dive into implementing any of these steps.

**How to Present It**:
Create a **GitHub repository** with a very clear structure and an excellent README.md file.

- README.md: This is your project's front page. Explain the project's purpose, the architecture (a simple diagram helps!), the tech stack you used, and clear instructions on how to set it up and run it (e.g., dbt run, docker build, docker run).

- Folder Structure:

/project-repo
├── dbt_project/      # Your dbt models and project files
├── app/              # Your Python API code (FastAPI/Flask)
│   ├── main.py
│   └── trained_model.pkl
├── scripts/          # Data ingestion and model training scripts
├── data/             # Sample source data
├── Dockerfile        # Docker instructions
└── README.md


## Progress:
- [x] Go to Kaggle.com, search "insurance fraud detection", found the most popular Notebook on this topic [Insurance Fraud Detection (Using 12 Models)](https://www.kaggle.com/code/niteshyadav3103/insurance-fraud-detection-using-12-models/input), downloaded the Input data to `data/insurance_claims.csv`.  

- [x] Following the Kaggle Notebook, I initially trained and compared 12 different models, selected *Ada Boost* as the best model (Fraud F1: 0.63, Fraud Recall: 0.66). Since the practices were not reasonable, I no longer use the `eda.ipynb` and the results `ada_boost_fraud_model.pkl`, `feature_scaler.pkl` and `model_metadate.json`, but archive them in `archive/`; the corresponding [prediction script for new data](prediction.py) is also archived. 

- [x] Retrain the model with `train_model.ipynb` and save the pipeline in `models/fraud_detection_pipeline.pkl`.

- [x] Build FastAPI (`main.py` and `pipeline_components.py`) for model serving in [text](app)

- [ ] Create data ingestion scripts

- [ ] Set up dbt for data transformation

- [ ] Containerize with Docker