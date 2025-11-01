# ============================================================================
# NSSM Service Installation Script for Clinic Cancellation Chatbot
# ============================================================================
# Run this script as Administrator on the production server

# Service configuration
$serviceName = "ClinicCancellationChatbot"
$serviceDisplayName = "Clinic Cancellation Chatbot"
$serviceDescription = "Automated SMS-based waitlist management for appointment cancellations"

# Paths (adjust if your installation directory is different)
$projectPath = "C:\Services\clinic_cancellation_chatbot"
$pythonExe = "$projectPath\.venv\Scripts\python.exe"
$appScript = "$projectPath\run.py"
$logPath = "$projectPath\data\logs"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Clinic Cancellation Chatbot - Service Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verify we're running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check if NSSM is installed
$nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssmPath) {
    Write-Host "❌ ERROR: NSSM not found" -ForegroundColor Red
    Write-Host "   Install NSSM from: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "   Or use Chocolatey: choco install nssm" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host "✅ NSSM found at: $($nssmPath.Source)" -ForegroundColor Green
Write-Host ""

# Check if project paths exist
if (-not (Test-Path $projectPath)) {
    Write-Host "❌ ERROR: Project path not found: $projectPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "❌ ERROR: Python executable not found: $pythonExe" -ForegroundColor Red
    Write-Host "   Make sure you've created the virtual environment:" -ForegroundColor Yellow
    Write-Host "   python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $appScript)) {
    Write-Host "❌ ERROR: Application script not found: $appScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Project path verified: $projectPath" -ForegroundColor Green
Write-Host "✅ Python executable found: $pythonExe" -ForegroundColor Green
Write-Host "✅ Application script found: $appScript" -ForegroundColor Green
Write-Host ""

# Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $logPath | Out-Null
Write-Host "✅ Log directory ready: $logPath" -ForegroundColor Green
Write-Host ""

# Check if service already exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "⚠️  Service '$serviceName' already exists" -ForegroundColor Yellow
    $response = Read-Host "   Do you want to reinstall it? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "   Stopping service..." -ForegroundColor Yellow
        nssm stop $serviceName 2>$null
        Start-Sleep -Seconds 2
        
        Write-Host "   Removing service..." -ForegroundColor Yellow
        nssm remove $serviceName confirm
        Start-Sleep -Seconds 1
        Write-Host "   ✅ Old service removed" -ForegroundColor Green
    } else {
        Write-Host "   Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Install service
Write-Host "📦 Installing service: $serviceName" -ForegroundColor Cyan
nssm install $serviceName $pythonExe $appScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to install service" -ForegroundColor Red
    exit 1
}

# Configure service
Write-Host "⚙️  Configuring service..." -ForegroundColor Cyan
nssm set $serviceName DisplayName $serviceDisplayName
nssm set $serviceName Description $serviceDescription
nssm set $serviceName AppDirectory $projectPath

# Environment variables
nssm set $serviceName AppEnvironmentExtra "PYTHONUNBUFFERED=1"
nssm set $serviceName AppEnvironmentExtra "ENVIRONMENT=production"

# Logging
nssm set $serviceName AppStdout "$logPath\service-stdout.log"
nssm set $serviceName AppStderr "$logPath\service-stderr.log"
nssm set $serviceName AppStdoutCreationDisposition 4  # Overwrite
nssm set $serviceName AppStderrCreationDisposition 4  # Overwrite

# Startup configuration
nssm set $serviceName Start SERVICE_AUTO_START
nssm set $serviceName AppRestartDelay 5000

# Failure handling
nssm set $serviceName AppExit Default Restart
nssm set $serviceName AppRestartDelay 5000
nssm set $serviceName AppThrottle 10000

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " ✅ Service installed successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service Name: $serviceName" -ForegroundColor White
Write-Host "Display Name: $serviceDisplayName" -ForegroundColor White
Write-Host "Python Path:  $pythonExe" -ForegroundColor White
Write-Host "Application:  $appScript" -ForegroundColor White
Write-Host "Logs:         $logPath" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure .env.production file is configured" -ForegroundColor White
Write-Host "  2. Start the service:" -ForegroundColor White
Write-Host "       nssm start $serviceName" -ForegroundColor Yellow
Write-Host "  3. Check service status:" -ForegroundColor White
Write-Host "       nssm status $serviceName" -ForegroundColor Yellow
Write-Host "  4. View logs:" -ForegroundColor White
Write-Host "       Get-Content $logPath\service-stdout.log -Tail 50" -ForegroundColor Yellow
Write-Host ""
