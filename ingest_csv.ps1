# Ingest PLFS CSV Data
# This script ingests both CSV files into the database

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PLFS CSV Data Ingestion" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Activate virtual environment
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "`nWarning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Check if CSV files exist
Write-Host "`nChecking CSV files..." -ForegroundColor Yellow

$chhv1 = Test-Path "chhv1.csv"
$cperv1 = Test-Path "cperv1.csv"

if (-not $chhv1) {
    Write-Host "  ✗ chhv1.csv not found" -ForegroundColor Red
}
if (-not $cperv1) {
    Write-Host "  ✗ cperv1.csv not found" -ForegroundColor Red
}

if (-not ($chhv1 -or $cperv1)) {
    Write-Host "`nNo CSV files found. Exiting." -ForegroundColor Red
    exit 1
}

# Show menu
Write-Host "`nAvailable datasets:" -ForegroundColor Yellow
Write-Host "  1. Household Survey (chhv1.csv) - 13 MB, ~102K rows" -ForegroundColor White
Write-Host "  2. Person Survey (cperv1.csv) - 118 MB, ~415K rows" -ForegroundColor White
Write-Host "  3. Both datasets" -ForegroundColor White
Write-Host "  4. Test verification only" -ForegroundColor White
Write-Host "  5. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`nIngesting Household Survey..." -ForegroundColor Green
        python ingest_csv_data.py --csv chhv1.csv --config config/datasets/household_survey.yaml
    }
    "2" {
        Write-Host "`nIngesting Person Survey..." -ForegroundColor Green
        Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
        python ingest_csv_data.py --csv cperv1.csv --config config/datasets/person_survey.yaml
    }
    "3" {
        Write-Host "`nIngesting both datasets..." -ForegroundColor Green
        Write-Host "This may take 10-15 minutes..." -ForegroundColor Yellow
        python ingest_plfs_data.py
    }
    "4" {
        Write-Host "`nRunning verification test..." -ForegroundColor Green
        python test_csv_ingestion.py
    }
    "5" {
        Write-Host "`nExiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "`nInvalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "Done! Check the output above for results." -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
