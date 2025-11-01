# ============================================================================
# Quick Update Script for Production Server
# ============================================================================
# This script pulls latest changes from GitHub and restarts the service

$serviceName = "ClinicCancellationChatbot"
$projectPath = "C:\Services\clinic_cancellation_chatbot"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Updating $serviceName" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
if (-not (Test-Path $projectPath)) {
    Write-Host "❌ Project path not found: $projectPath" -ForegroundColor Red
    exit 1
}

Set-Location $projectPath

# Check if service exists
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if (-not $service) {
    Write-Host "❌ Service '$serviceName' not found" -ForegroundColor Red
    Write-Host "   Run install_service.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Stop service
Write-Host "⏸️  Stopping service..." -ForegroundColor Yellow
nssm stop $serviceName
Start-Sleep -Seconds 3

$status = nssm status $serviceName
Write-Host "   Service stopped: $status" -ForegroundColor Gray
Write-Host ""

# Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  WARNING: You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus -ForegroundColor Gray
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Update cancelled." -ForegroundColor Yellow
        nssm start $serviceName
        exit 0
    }
}

# Store current commit hash for rollback
$previousCommit = git rev-parse HEAD
Write-Host "📍 Current commit: $($previousCommit.Substring(0,7))" -ForegroundColor Gray

# Pull changes
Write-Host "📥 Pulling latest changes from GitHub..." -ForegroundColor Cyan
git pull origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git pull failed" -ForegroundColor Red
    Write-Host "   Starting service with current code..." -ForegroundColor Yellow
    nssm start $serviceName
    exit 1
}

$newCommit = git rev-parse HEAD
if ($previousCommit -eq $newCommit) {
    Write-Host "✅ Already up to date (no changes)" -ForegroundColor Green
} else {
    Write-Host "✅ Updated to: $($newCommit.Substring(0,7))" -ForegroundColor Green
    
    # Show what changed
    Write-Host ""
    Write-Host "📝 Changes:" -ForegroundColor Cyan
    git log --oneline $previousCommit..$newCommit | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
}

Write-Host ""

# Check if requirements.txt changed
$changedFiles = git diff --name-only $previousCommit $newCommit
$requirementsChanged = $changedFiles | Select-String "requirements.txt"

if ($requirementsChanged) {
    Write-Host "📦 requirements.txt changed - updating dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Dependencies updated" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Dependency update had issues" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Check if schema changed (would need migration)
$schemaChanged = $changedFiles | Select-String "schema.sql"
if ($schemaChanged) {
    Write-Host "⚠️  Database schema changed!" -ForegroundColor Yellow
    Write-Host "   You may need to run migrations" -ForegroundColor Yellow
    Write-Host ""
}

# Start service
Write-Host "▶️  Starting service..." -ForegroundColor Cyan
nssm start $serviceName
Start-Sleep -Seconds 5

# Check status
$status = nssm status $serviceName
Write-Host ""

if ($status -eq "SERVICE_RUNNING") {
    Write-Host "============================================" -ForegroundColor Green
    Write-Host " ✅ Update complete! Service is running." -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Monitor logs with:" -ForegroundColor Cyan
    Write-Host "  Get-Content data\logs\service-stdout.log -Tail 50 -Wait" -ForegroundColor Yellow
} else {
    Write-Host "============================================" -ForegroundColor Red
    Write-Host " ❌ Service failed to start" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Cyan
    Write-Host "  Get-Content data\logs\service-stderr.log -Tail 50" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To rollback:" -ForegroundColor Cyan
    Write-Host "  git checkout $($previousCommit.Substring(0,7))" -ForegroundColor Yellow
    Write-Host "  nssm start $serviceName" -ForegroundColor Yellow
}
