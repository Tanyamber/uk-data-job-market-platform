import os
import sys
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery
from google.oauth2 import service_account

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.config import (
    ADZUNA_APP_ID, ADZUNA_APP_KEY, COUNTRY_CODE, 
    SEARCH_KEYWORDS, GCP_PROJECT_ID, 
    RAW_DATASET_ID, RAW_TABLE_ID
)

def get_bq_client():
    credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gcp_credentials.json")
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"❌ [ERROR] Security key missing at: {credentials_path}")
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    return bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)

def scrape_full_description(url):
    """
    Helper Scraper: Navigates to the live redirect URL, downloads the HTML body,
    and cleanly extracts all human-readable text blocks, dropping HTML garbage.
    """
    if not url:
        return None
    try:
        # Standard browser headers to ensure the remote server accepts our connection handshake
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract plain text content and strip out unnecessary whitespaces
            clean_text = soup.get_text(separator=' ', strip=True)
            # Truncate text block slightly if it's abnormally massive to maintain free-tier warehouse limits
            return clean_text[:6000]
    except Exception:
        pass # If a single company site blocks scrapers, gracefully pass so the script keeps running
    return None

def extract_live_uk_jobs(max_pages_per_keyword=1):
    all_jobs = []
    
    for keyword in SEARCH_KEYWORDS:
        print(f"🚀 [INIT] Extracting live postings for keyword segment: '{keyword}'...")
        
        for page in range(1, max_pages_per_keyword + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY_CODE}/search/{page}"
            params = {
                'app_id': ADZUNA_APP_ID,
                'app_key': ADZUNA_APP_KEY,
                'what': keyword,
                'results_per_page': 10, # Kept at 10 rows per page to prevent scraping speed blocks
                'content-type': 'application/json'
            }
            
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                
                for job in results:
                    job_url = job.get('redirect_url')
                    print(f"🔗 [SCRAPE] Extracting full text body from original source link...")
                    full_desc = scrape_full_description(job_url)
                    
                    # Fallback to the short snippet if the remote job board completely blocks scraping
                    final_desc = full_desc if full_desc else job.get('description')
                    
                    job_record = {
                        'job_id': str(job.get('id')),
                        'search_keyword': keyword,
                        'title': job.get('title'),
                        'description': final_desc, # Contains our deep-text full description!
                        'job_url': job_url,        # NEW: Stored for direct job applications!
                        'salary_min': float(job.get('salary_min')) if job.get('salary_min') is not None else None,
                        'salary_max': float(job.get('salary_max')) if job.get('salary_max') is not None else None,
                        'company': job.get('company', {}).get('display_name'),
                        'city': job.get('location', {}).get('area', [])[-1] if job.get('location', {}).get('area') else None,
                        'county': job.get('location', {}).get('area', [])[1] if len(job.get('location', {}).get('area', [])) > 1 else None,
                        'created': job.get('created'),
                        'contract_time': job.get('contract_time'),
                        'contract_type': job.get('contract_type'),
                        'category': job.get('category', {}).get('label')
                    }
                    all_jobs.append(job_record)
                    time.sleep(1) # Courteous sleep delay to preserve network safety thresholds
                
                print(f"📥 [FETCH] Extracted {len(results)} scraped jobs for '{keyword}' (Page {page}).")
                
            except Exception as e:
                print(f"❌ [FATAL] Failed page {page}: {e}")
                
            time.sleep(1)
            
    return pd.DataFrame(all_jobs)

def load_to_bigquery(df):
    if df.empty:
        return
    client = get_bq_client()
    dataset_ref = bigquery.DatasetReference(GCP_PROJECT_ID, RAW_DATASET_ID)
    table_ref = dataset_ref.table(RAW_TABLE_ID)
    
    # Enable schema evolution so BigQuery automatically adds our new 'job_url' column!
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
    )
    
    print(f"⚡ [LOAD] Delivery processing: Streaming {len(df)} scraped rows into BigQuery...")
    load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    load_job.result()
    print("🔥 [SUCCESS] Scraped data vertical stream complete.")

if __name__ == "__main__":
    combined_market_data = extract_live_uk_jobs(max_pages_per_keyword=1)
    load_to_bigquery(combined_market_data)