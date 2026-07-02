with job_skills_data as (
    select * from {{ ref('int_job_skills') }} -- Referencing our skill layer
),

final_mart_metrics as (
    select
        job_id,
        job_category,
        job_title,
        company,
        job_url,
        city,
        county,
        posted_date,
        
        -- Base Salary Metrics
        salary_min,
        salary_max,
        -- Calculate the statistical midpoint salary for clean dashboard sorting
        round((salary_min + salary_max) / 2, 2) as salary_midpoint,
        
        -- Boolean Skills Mapping (Making them highly readable for Power BI charts)
        has_python,
        has_sql,
        has_dbt,
        has_power_bi,
        has_aws,
        has_excel,
        has_spark

    from job_skills_data
    -- Quality Control: Filter out postings that do not include salary information
    where salary_min is not null or salary_max is not null
)

select * from final_mart_metrics