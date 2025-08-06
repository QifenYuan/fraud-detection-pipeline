-- models/staging/stg_claims.sql

-- This model selects all columns from the raw claims data and performs type casting only, 
-- matching the result of pandas read_csv.

-- Note: DuckDB will automatically store date strings as datetime64[us], to avoid this, 
-- we cast the date columns to varchar. 

with source as (
    select * from read_csv_auto('../data/source/claims_batch_*.csv', header=true)
),
typed as (
    select
        cast(months_as_customer as integer) as months_as_customer,
        cast(age as integer) as age,
        cast(policy_number as integer) as policy_number,
        cast(policy_bind_date as varchar) as policy_bind_date,
        policy_state,
        policy_csl,
        cast(policy_deductable as integer) as policy_deductable,
        cast(policy_annual_premium as double) as policy_annual_premium,
        cast(umbrella_limit as integer) as umbrella_limit,
        cast(insured_zip as integer) as insured_zip,
        insured_sex,
        insured_education_level,
        insured_occupation,
        insured_hobbies,
        insured_relationship,
        cast("capital-gains" as integer) as capital_gains,
        cast("capital-loss" as integer) as capital_loss,
        cast(incident_date as varchar) as incident_date,
        incident_type,
        collision_type,
        incident_severity,
        authorities_contacted,
        incident_state,
        incident_city,
        incident_location,
        cast(incident_hour_of_the_day as integer) as incident_hour_of_the_day,
        cast(number_of_vehicles_involved as integer) as number_of_vehicles_involved,
        property_damage,
        cast(bodily_injuries as integer) as bodily_injuries,
        cast(witnesses as integer) as witnesses,
        police_report_available,
        cast(total_claim_amount as integer) as total_claim_amount,
        cast(injury_claim as integer) as injury_claim,
        cast(property_claim as integer) as property_claim,
        cast(vehicle_claim as integer) as vehicle_claim,
        auto_make,
        auto_model,
        cast(auto_year as integer) as auto_year,
        fraud_reported,
        cast(_c39 as double) as _c39
    from source
)
select * from typed
