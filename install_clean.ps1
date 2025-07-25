# install_clean.ps1
# Clean pip cache, temp files, and install requirements safely

Write-Host "`n[CLEAN] Purging pip cache..." -ForegroundColor Cyan
pip cache purge

Write-Host "`n[CLEAN] Removing pip temporary unpack files..." -ForegroundColor Cyan
$TempPath = $env:TEMP
Get-ChildItem -Path $TempPath -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "pip-unpack-*" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n[ENV] Activating virtual environment..." -ForegroundColor Cyan
$envPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $envPath) {
    & $envPath
    Write-Host "[OK] Virtual environment activated." -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Virtual environment not found at $envPath. Exiting..." -ForegroundColor Red
    exit 1
}

# Optional: Pre-install xgboost manually if wheel is present
$xgbWheel = "xgboost-3.0.2-py3-none-win_amd64.whl"
if (Test-Path $xgbWheel) {
    Write-Host "`n[INSTALL] Found xgboost wheel. Installing locally..." -ForegroundColor Cyan
    pip install $xgbWheel

    # Remove xgboost from requirements.txt to avoid re-install
    Write-Host "`n[EDIT] Removing xgboost from requirements.txt temporarily..." -ForegroundColor Cyan
    (Get-Content requirements.txt) | Where-Object { $_ -notmatch "xgboost" } | Set-Content requirements-temp.txt
    Move-Item -Force requirements-temp.txt requirements.txt
} else {
    Write-Host "`n[SKIP] xgboost wheel not found. Skipping..." -ForegroundColor Yellow
}

Write-Host "`n[INSTALL] Installing other requirements from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt --no-cache-dir

Write-Host "`n[FINISHED] All steps completed successfully." -ForegroundColor Green