with staging_data as (
    select * from {{ ref('stg_jobs') }}
),

extract_skills as (
    select
        job_id,
        job_category,
        job_title,
        company,
        job_url,
        salary_min,
        salary_max,
        city,
        county,
        posted_date,
        
        -- Upgraded Analytics: Scan BOTH job_title AND job_description snippet for maximum reach
        case 
            when lower(job_description) like '%python%' 
                 or lower(job_title) like '%python%' 
            then 1 else 0 
        end as has_python,
        
        case 
            when lower(job_description) like '%sql%' 
                 or lower(job_description) like '%database%'
                 or lower(job_title) like '%sql%' 
            then 1 else 0 
        end as has_sql,
        
        case 
            when lower(job_description) like '%dbt%' 
                 or lower(job_description) like '%data build tool%'
                 or lower(job_title) like '%dbt%' 
            then 1 else 0 
        end as has_dbt,
        
        case 
            when lower(job_description) like '%power bi%' 
                 or lower(job_description) like '%powerbi%' 
                 or lower(job_title) like '%power bi%'
                 or lower(job_title) like '%powerbi%'
            then 1 else 0 
        end as has_power_bi,
        
        case 
            when lower(job_description) like '%aws%' 
                 or lower(job_description) like '%cloud%'
                 or lower(job_title) like '%aws%' 
                 or lower(job_title) like '%cloud%'
            then 1 else 0 
        end as has_aws,
        
        case 
            when lower(job_description) like '%excel%' 
                 or lower(job_title) like '%excel%' 
            then 1 else 0 
        end as has_excel,
        
        case 
            when lower(job_description) like '%spark%' 
                 or lower(job_description) like '%pyspark%'
                 or lower(job_title) like '%spark%' 
            then 1 else 0 
        end as has_spark

    from staging_data
)

select * from extract_skills