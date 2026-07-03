@echo off
:: Force the Windows Command Prompt to use UTF-8 encoding mode
chcp 65001 > nul

:: Force Python to enforce UTF-8 for all file and terminal outputs
set PYTHONIOENCODING=utf-8

echo =================================================== >> logs\pipeline_execution.log
echo 📅 RUN STARTED AT: %date% %time% >> logs\pipeline_execution.log
echo =================================================== >> logs\pipeline_execution.log

:: ──► PHASE 1: NAVIGATE AND RUN PYTHON INGESTION ENGINE ◄──
cd /d "C:\DE_Portfolio\uk-data-job-market-platform"
echo 🚀 Launching Python Ingestion Scraper... >> logs\pipeline_execution.log
"C:\Python314\python.exe" prefect/daily_flow.py >> logs\pipeline_execution.log 2>&1

:: ──► PHASE 2: NAVIGATE AND RUN dbt ANALYTICAL TRANSFORMATIONS ◄──
cd /d "C:\DE_Portfolio\uk-data-job-market-platform\dbt\uk_market_transform"
echo 📈 Launching dbt Analytical Transformation Layers... >> logs\pipeline_execution.log
"C:\Users\prata\AppData\Roaming\Python\Python314\Scripts\dbt.exe" run >> ..\..\logs\pipeline_execution.log 2>&1

echo 🏁 RUN FINISHED COMFORTABLY AT: %time% >> ..\..\logs\pipeline_execution.log
exit