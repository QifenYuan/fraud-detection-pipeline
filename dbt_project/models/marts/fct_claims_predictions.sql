-- models/marts/fct_claims_predictions.sql

-- This model simply returns all columns from stg_claims as is, with no transformation.

select * from {{ ref('stg_claims') }}
