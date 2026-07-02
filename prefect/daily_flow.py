import os
import sys
from prefect import flow, task

# Route paths so Prefect can find your ingestion code cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.fetch_jobs import extract_live_uk_jobs, load_to_bigquery

@task(retries=3, retry_delay_seconds=10, name="API-Extraction")
def run_extraction_task():
    """Wrapped task that extracts 5 pages of multi-vertical listings."""
    # Pulls a rich 5-page sample per keyword segment
    df = extract_live_uk_jobs(max_pages_per_keyword=5)
    return df

@task(retries=2, retry_delay_seconds=15, name="Warehouse-Loading")
def run_loading_task(df):
    """Wrapped task that pushes the parsed records into BigQuery."""
    load_to_bigquery(df)

@flow(name="UK-Data-Market-Daily-ELT")
def uk_market_pipeline_flow():
    """
    The master orchestration controller for your data platform.
    """
    print("🎬 [ORCHESTRATOR] Initializing Prefect Cloud flow workflow engine...")
    
    # Run Stage 1
    raw_job_data = run_extraction_task()
    
    # Run Stage 2
    run_loading_task(raw_job_data)
    
    print("🏁 [ORCHESTRATOR] Flow iteration fully completed successfully.")

if __name__ == "__main__":
    # Test execute the orchestrator locally
    uk_market_pipeline_flow()