with raw_source as (
    select * from {{ source('raw_market_intelligence', 'raw_jobs') }}
),

clean_and_indexed as (
    select
        cast(job_id as string) as job_id,
        lower(search_keyword) as job_category,
        title as job_title,
        company,
        description as job_description,
        job_url, -- Pulling the active URL value out of raw
        salary_min,
        salary_max,
        city,
        county,
        contract_time,
        contract_type,
        cast(left(created, 10) as date) as posted_date,
        
        row_number() over (
            partition by job_id 
            order by created desc
        ) as row_num

    from raw_source
)

select
    job_id,
    job_category,
    job_title,
    company,
    job_description,
    job_url, -- Expose to intermediate
    salary_min,
    salary_max,
    city,
    county,
    contract_time,
    contract_type,
    posted_date
from clean_and_indexed
where row_num = 1