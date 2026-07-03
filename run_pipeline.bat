@echo off
:: Force the Windows Command Prompt to use UTF-8 encoding mode
chcp 65001 > nul

:: Force Python to enforce UTF-8 for all file and terminal outputs
set PYTHONIOENCODING=utf-8

:: Navigate cleanly into your local data project directory
cd /d "C:\DE_Portfolio\uk-data-job-market-platform"

:: Execute your Prefect orchestrated python pipeline using your exact system Python engine
"C:\Python314\python.exe" prefect/daily_flow.py >> logs\pipeline_execution.log 2>&1

:: Exit gracefully once the streaming upload completes
exit