VISION.md

# 20250805 (TUE)

## Data Transformation -- re-implement dbt models

- [done!] Decide: **Where should we do "all the preprocessing steps"**, in the sklearn pipeline or the dbt marts model?

  - choose **the sklearn pipeline**, because
    - should be tightly coupled with the ML model, ensuring consistency between training and inference
    - will deploy the model in an API, want to avoid duplicating logic between dbt and Python
    - want to use sklearn's pipeline features, such as cross-validation, hyperparameter tuning, and reproducibility.    

  - otherwise, use **the dbt marts model** when
    - need a single, clean, ready-to-use dataset for multiples downstream consumers, not just ML, but BI, analytics, etc
    - your feature engineering logic is SQL-friendly, or easier to maintain in dbt, such as joins, window functions, or business logic
    - want to decouple data transformation from model training, making the pipeline more modular

  - In practice, *for ML applications*, it’s common to do basic cleaning and type casting in dbt, but keep model-specific feature engineering (like custom features, column renaming, etc.) in the sklearn pipeline. This ensures that the exact same logic is applied at inference time.

- [done!] Decide: `dbt_project/models/` must be simple
  - `stg_claims.sql`: select all 40 columns, do type casting 
  - `fct_claims_predictions.sql`: nothing
  - they together should give me the same result as a simple `df = pd.read_csv('data/train_claims.csv')` can do

- [done!] Modify `models/staging/stg_claims.sql` so that it selects all 40 columns and performs type casting based on the output of `df.info()`.

- [done!] Modify `models/marts/fct_claims_predictions.sql` so that it does nothing to the input, and return them "as is"

- [done!] Run in Terminal `cd dbt_project && dbt run` to update `fraud_detection_db.duckdb`

## Model Training -- add `FeatureEngineer` in the model pipeline

- [done!] Update `dbt_model_training.ipynb`, the goal is to save *all steps* in the model pipeline.  
  
  - [done!] Test loading data from  `fraud_detection_db.duckdb`. Slightly different data type, e.g. `months_as_customer` is `int32`, and `int64` if we read the csv with pandas directly. -- Igore it, as we do not have values greater than 2,147,483,647.    
  
  - Add the `FeatureEngineer` step (as a class) to model pipeline, specifically, include the "columns_to_drop" list as an **init** parameter of the class, so that it will also get saved.   

- [done!] Run `dbt_model_training.ipynb`, and update `models/dbt_fraud_detection_pipeline.pkl`

## Prediction Service - update the API app 

- the goal: An API serves the latest trained model, ready to make predictions on new, individual claims. 

- [done!] Re-write `app/main.py` to match the new `models/dbt_fraud_detection_pipeline.pkl` that has the entire model pipeline. Move the old to "archive/app/main.py".
  - The number of input variables in class Claim(BaseModel) equal to 39? - yes
  - OK to have a variable name starting with a "_" in "_c39"? - yes, will work for Pydantic and DataFrame, but it often used to indicate a "private" or internal variable in Python, so some libraries may get confused, *should be careful*. Besides, our model pipeline will drop it during FeatureEngineer anyway, so, I deleted it.
  - The original csv file has two columns with "-" in their names ("capital-gains" and "capital-loss") and the new data may be provided like this also. Should make the "class Claim(BaseModel)" part flexible to accept this.

- [done!] Save two real rows from original csv to JSON files, see `test_samples/sample_1.json`

- How to Run the API server?   
  - Make sure to activate venv, in root directory in Terminal type `source .venv/bin/activate`
  - Then type `uvicorn app.main:app --reload`

- [done!] Handle the Issue with `FeatureEngineer` being a *custom class*, whereas `joblib` (in `app/main.py`) needs to import it from the same module, with the same name when loading the model. 
  - create `app/feature_engineer.py` and copy the class definition there. 
  - import it in `app/main.py`. 
  - import it in also `dbt_model_training.ipynb`, re-train and save the updated model pipeline in `models/dbt_fraud_detection_pipeline.pkl`.
  - Re-run showed "Application startup complete." - success! 


- 3 ways to send POST requests to the `/predict` endpoint with your sample JSON files to get predictions?

  - First, run API server
  
  - Option 1: Using curl: In Terminal,

    curl -X POST "http://127.0.0.1:8000/predict" \
        -H "Content-Type: application/json" \
        -d @test_samples/sample_1.json

  - Option 2: Using httpie: also in Terminal? `http POST http://127.0.0.1:8000/predict < test_samples/sample_1.json` (my zsh does not recognize 'http')

  - Option 3: Postman (chosen!)


- How to create a new POST request to http://127.0.0.1:8000/predict in Postman? (downloaded & installed, qifenyuan@gmail.com, pw by Duck)
   1. Open Postman.
   2. Click the "New" button or the "+" tab to open a new request tab.
   3. Set the request type to POST (dropdown to the left of the URL bar).
   4. Enter http://127.0.0.1:8000/predict in the URL bar.
   5. Click the "Body" tab below the URL bar.
   6. Select "raw" and then choose "JSON" from the dropdown on the right.
   7. Paste your sample JSON (e.g., from test_samples/sample_1.json) into the text area.
   8. Click the "Send" button.


- [done!] Handle the **Issue with different test samples returned identical prediction through API**, found the pipeline and API are working as intended!
  - Both {"prediction": "N", "probability": 0.8807970779778823}
  - Add logging to `app/main.py` (Line 75-86), see if any difference after the `FeatureEngineer` step, before prediction.
  - Update `dbt_model_training.ipynb` (Line 10 and Line 42) to resolve the name mismatch with `app/main.py`. Re-trained and re-saved the model. 
  - Saw the transformed features indeed clearly different.
  - Finding: **The problem is with my model**, it may not be sensitive enough to the differences, or the class distribution/feature importance in your training data leads to similar outputs.     


# 20250806 (WED)

## Present it on GitHub 

Thank you very much for the notebook! However, since I'm looking for a job, I've decided to present the existing project on GitHub first, and find time to improve model sensitivity later on. Could you please help me build a professional GitHub repository?   

### [done!] Folder Structure

fraud-detection-pipeline/
├── README.md
├── LICENSE
├── .gitignore
├── dbt_project/                  # dbt models and configs
│   ├── models/
│   ├── dbt_project.yml
│   └── ... (other dbt files)
├── app/                          # FastAPI app and model code
│   ├── main.py
│   ├── feature_engineer.py
│   └── __init__.py
├── models/                       # Trained model artifacts
│   └── dbt_fraud_detection_pipeline.pkl
├── scripts/                      # Data ingestion
│   └── ingest_data.py
├── data/                         # Sample and raw data
│   ├── source/                   # dbt raw data source (created by ingest_data.py)
│   └── raw/
│       ├── new_claims/           # Drop new claim CSVs here for ingestion
│       └── processed_claims/     # Ingested files are moved here
│   └── test_samples/
│       ├── sample_1.json
│       └── sample_2.json
├── requirements.txt              # Python dependencies
├── dbt_model_training.ipynb      # Main model training notebook
├── model_sensitivity_analysis.ipynb  # (Optional, for future work)
└── Dockerfile                    # (Optional, for containerization)


### Additional Tips
- gitignore
- use clear commit messages, a clean commit history
- push only necessary data (no large raw dataset or secrets)
- [done!] add comments and docstrings to my code.
- [done!] Have a LICENSE file in the repo


### [done!] README, Run-through the whole project to validate locally
- Go through README.md section by section:
  - [done!] Getting Started: 
    - requirements.txt: complete and professional!
    - `dbt_model_training.ipynb`: added to the Folder Structure

- [done!] Re-run the whole project:
  - [Exclude!] python scripts/generate_new_data.py: [simulation_claims.csv](data/simulation_claims.csv) -> 20 csv files in `data/raw/new_claims/`
  - Include the Data Ingestion step: python scripts/ingest_data.py: `data/raw/new_claims/` -> a new claims batch in `data/source/`. Ctrl + c
  - edit and run `dbt_model_training.ipynb`, convert Y/N to 1/0
  - update `app/main.py`
  - start the API server 
  - test a sample on Postman

### Publishing on GitHub

#### 1. Create a New GitHub Repository

1. Go to https://github.com and log in.
2. Click the "+" icon in the top right and select "New repository".
3. Name your repository (e.g., `fraud-detection-pipeline`).
4. (Optional) Add a description.
5. Set visibility to Public or Private as you prefer.
6. **Do not** initialize with a README, .gitignore, or license (you already have these).
7. Click "Create repository".

---

#### 2. Initialize Local Git Repository

In your project root directory, run:

```bash
git init
git add .
git commit -m "Initial commit: add project files"
```

---

#### 3. Add Remote and Push

Copy the remote URL from your new GitHub repo (e.g., `https://github.com/yourusername/fraud-detection-pipeline.git`), then run:

```bash
git remote add origin https://github.com/yourusername/fraud-detection-pipeline.git
git branch -M main
git push -u origin main
```

---

#### 4. Verify on GitHub

- Go to your repository page on GitHub.
- Refresh and check that all files and folders are present and formatted correctly.

---

#### 5. (Optional) Add Topics, Description, and Social Links

- On your repo page, click the gear/settings icon to add topics (e.g., `mlops`, `fraud-detection`, `fastapi`, `dbt`).
- Add a project description and website/LinkedIn if desired.

---

#### 6. (Optional) Set Up Repository Features

- Enable Issues and Discussions if you want community feedback.
- Set up GitHub Actions for CI/CD if you want automated testing.

---

You’re done! Your project is now live and shareable. If you need help with any step or want to automate some of this, let me know!

# 20250807 (THU)

## [Next] Model Training - improve model sensitivity**, create `model_sensitivity_analysis.ipynb`: 
  - consider:
    - Retraining with more data or different features.
    - Trying a more complex model.
    - Examining feature importances to see what drives predictions.


