# 🚀 DEPLOYMENT GUIDE - Windows Server with NSSM

**Target Environment:** Windows Server (on-premises)  
**Service Manager:** NSSM (Non-Sucking Service Manager)  
**Deployment Model:** Git-based (develop locally → push → pull on server)

---

## 📋 Overview

This guide covers deploying the Clinic Cancellation Chatbot as a Windows service using NSSM. The deployment workflow is:

1. **Develop & test** on local laptop
2. **Commit & push** to GitHub
3. **Pull & restart** on production server

---

## 🔧 Server Prerequisites

### Required Software
- [x] Windows Server 2016+ (or Windows 10/11 Pro)
- [x] Python 3.11 or higher
- [x] Git for Windows
- [x] NSSM (Non-Sucking Service Manager)
- [x] PostgreSQL 14+ (already running at 192.168.1.220:5432)

### Install NSSM

**Option 1: Download directly**
```powershell
# Download from: https://nssm.cc/download
# Extract to: C:\Tools\nssm\
# Add to PATH: C:\Tools\nssm\win64
```

**Option 2: Using Chocolatey**
```powershell
choco install nssm
```

---

## 📦 Initial Server Setup

### 1. Clone Repository

```powershell
# Navigate to deployment location
cd C:\Services

# Clone repository
git clone https://github.com/dollythedog/clinic_cancellation_chatbot.git
cd clinic_cancellation_chatbot
```

### 2. Create Virtual Environment

```powershell
# Create venv
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Production Environment

```powershell
# Copy production template
Copy-Item .env.example .env.production

# Edit .env.production with production values
notepad .env.production
```

**Production .env values:**
```bash
# Database (production server)
DATABASE_URL=postgresql://postgres:{{PASSWORD}}@192.168.1.220:5432/clinic_chatbot

# Twilio (production credentials)
USE_MOCK_TWILIO=false
ENABLE_SMS_SENDING=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN={{PRODUCTION_TOKEN}}
TWILIO_PHONE_NUMBER=+12145551234
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Webhooks (production URL - Cloudflare Tunnel or Tailscale)
TWILIO_WEBHOOK_BASE_URL=https://your-production-url.com
WEBHOOK_SIGNATURE_ENABLED=true

# Application
BATCH_SIZE=3
HOLD_MINUTES=7
CONTACT_HOURS_START=08:00
CONTACT_HOURS_END=20:00
TIMEZONE=America/Chicago

# Production settings
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=C:\Services\clinic_cancellation_chatbot\data\logs\app.log

# Enable all features
ENABLE_SMS_SENDING=true
ENABLE_WEBHOOKS=true
ENABLE_AUTO_CONFIRMATION=true
ENABLE_PRIORITY_RECALC=true
```

### 4. Test Server Connection

```powershell
# Test database connection
python -c "from app.infra.db import check_db_connection; print('✅ Connected!' if check_db_connection() else '❌ Failed')"

# Test application startup
python run.py
# Press Ctrl+C to stop after verifying it starts
```

---

## 🔐 NSSM Service Installation

### 1. Create Service Installation Script

Create `scripts/install_service.ps1`:

```powershell
# Service configuration
$serviceName = "ClinicCancellationChatbot"
$serviceDisplayName = "Clinic Cancellation Chatbot"
$serviceDescription = "Automated SMS-based waitlist management for appointment cancellations"

# Paths (adjust if different)
$projectPath = "C:\Services\clinic_cancellation_chatbot"
$pythonExe = "$projectPath\.venv\Scripts\python.exe"
$appScript = "$projectPath\run.py"
$logPath = "$projectPath\data\logs"
$envFile = "$projectPath\.env.production"

# Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $logPath

# Stop and remove existing service if it exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Stopping existing service..."
    nssm stop $serviceName
    Write-Host "Removing existing service..."
    nssm remove $serviceName confirm
}

# Install service
Write-Host "Installing service: $serviceName"
nssm install $serviceName $pythonExe $appScript

# Configure service
nssm set $serviceName DisplayName $serviceDisplayName
nssm set $serviceName Description $serviceDescription
nssm set $serviceName AppDirectory $projectPath
nssm set $serviceName AppEnvironmentExtra "PYTHONUNBUFFERED=1"
nssm set $serviceName AppEnvironmentExtra "ENVIRONMENT=production"

# Logging
nssm set $serviceName AppStdout "$logPath\service-stdout.log"
nssm set $serviceName AppStderr "$logPath\service-stderr.log"
nssm set $serviceName AppStdoutCreationDisposition 4
nssm set $serviceName AppStderrCreationDisposition 4

# Startup configuration
nssm set $serviceName Start SERVICE_AUTO_START
nssm set $serviceName AppRestartDelay 5000

# Failure handling
nssm set $serviceName AppExit Default Restart
nssm set $serviceName AppRestartDelay 5000
nssm set $serviceName AppThrottle 10000

Write-Host "✅ Service installed successfully!"
Write-Host ""
Write-Host "To start the service, run:"
Write-Host "  nssm start $serviceName"
Write-Host ""
Write-Host "To check service status:"
Write-Host "  nssm status $serviceName"
```

### 2. Install the Service

```powershell
# Run as Administrator
cd C:\Services\clinic_cancellation_chatbot
.\scripts\install_service.ps1
```

### 3. Start the Service

```powershell
# Start service
nssm start ClinicCancellationChatbot

# Check status
nssm status ClinicCancellationChatbot

# View logs
Get-Content data\logs\service-stdout.log -Tail 50
```

---

## 🔄 Update Workflow

### From Development Laptop

```powershell
# 1. Make changes locally
# 2. Test locally (python run.py)
# 3. Commit changes
git add -A
git commit -m "feat: description of changes"

# 4. Push to GitHub
git push
```

### On Production Server

```powershell
# Navigate to project directory
cd C:\Services\clinic_cancellation_chatbot

# Stop the service
nssm stop ClinicCancellationChatbot

# Pull latest changes
git pull origin main

# Update dependencies (if requirements.txt changed)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run any database migrations (if needed)
# alembic upgrade head

# Start the service
nssm start ClinicCancellationChatbot

# Verify service is running
nssm status ClinicCancellationChatbot

# Check logs for errors
Get-Content data\logs\service-stdout.log -Tail 50
```

### Quick Update Script

Create `scripts/update_server.ps1`:

```powershell
# Quick update script for production server
$serviceName = "ClinicCancellationChatbot"

Write-Host "🔄 Updating $serviceName..."

# Stop service
Write-Host "Stopping service..."
nssm stop $serviceName
Start-Sleep -Seconds 3

# Pull changes
Write-Host "Pulling latest changes from GitHub..."
git pull origin main

# Check if requirements changed
$requirementsChanged = git diff HEAD@{1} --name-only | Select-String "requirements.txt"
if ($requirementsChanged) {
    Write-Host "Installing updated dependencies..."
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Start service
Write-Host "Starting service..."
nssm start $serviceName
Start-Sleep -Seconds 5

# Check status
$status = nssm status $serviceName
Write-Host "Service status: $status"

if ($status -eq "SERVICE_RUNNING") {
    Write-Host "✅ Update complete! Service is running."
} else {
    Write-Host "❌ Service failed to start. Check logs:"
    Write-Host "   Get-Content data\logs\service-stderr.log -Tail 50"
}
```

Usage:
```powershell
.\scripts\update_server.ps1
```

---

## 🔍 Service Management

### Common Commands

```powershell
# Start service
nssm start ClinicCancellationChatbot

# Stop service
nssm stop ClinicCancellationChatbot

# Restart service
nssm restart ClinicCancellationChatbot

# Check status
nssm status ClinicCancellationChatbot

# View service configuration
nssm dump ClinicCancellationChatbot

# Edit service configuration
nssm edit ClinicCancellationChatbot

# Remove service (if needed)
nssm remove ClinicCancellationChatbot confirm
```

### Viewing Logs

```powershell
# Application logs
Get-Content data\logs\app.log -Tail 100 -Wait

# Service stdout
Get-Content data\logs\service-stdout.log -Tail 100 -Wait

# Service stderr (errors)
Get-Content data\logs\service-stderr.log -Tail 100 -Wait
```

---

## 🌐 Network Configuration

### Webhook Exposure Options

The server needs to receive webhooks from Twilio. Choose one:

**Option 1: Cloudflare Tunnel (Recommended)**
```powershell
# Install cloudflared
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Run tunnel
cloudflared tunnel --url http://localhost:8000
# Copy the public URL to .env.production (TWILIO_WEBHOOK_BASE_URL)
```

**Option 2: Tailscale Funnel**
```powershell
# Install Tailscale
# Enable funnel
tailscale funnel 8000
```

**Option 3: Direct Port Forwarding**
- Configure router to forward port 8000 to server
- Set up static IP or dynamic DNS
- Configure firewall rules

---

## 🔐 Security Checklist

### Server Hardening
- [ ] Run service as dedicated user (not Administrator)
- [ ] Set appropriate file permissions on project directory
- [ ] Enable Windows Firewall with only necessary ports open
- [ ] Keep Windows Server updated
- [ ] Configure automatic security updates

### Application Security
- [ ] Use strong passwords in .env.production
- [ ] Never commit .env.production to Git
- [ ] Enable webhook signature verification
- [ ] Use HTTPS for webhook URLs
- [ ] Implement rate limiting in production
- [ ] Regular log monitoring and rotation

### Database Security
- [ ] Use dedicated database user (not postgres)
- [ ] Principle of least privilege (only required permissions)
- [ ] Enable SSL connections to database
- [ ] Regular backups configured
- [ ] Database encryption at rest enabled

---

## 📊 Monitoring

### Health Checks

```powershell
# Check if service is running
nssm status ClinicCancellationChatbot

# Check API health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content

# Check database connection
python -c "from app.infra.db import check_db_connection; print('✅ DB OK' if check_db_connection() else '❌ DB Failed')"
```

### Scheduled Health Checks

Create a scheduled task to monitor the service:

```powershell
# Create health check script: scripts/health_check.ps1
$serviceName = "ClinicCancellationChatbot"
$status = nssm status $serviceName

if ($status -ne "SERVICE_RUNNING") {
    Write-Host "❌ Service is not running. Attempting restart..."
    nssm start $serviceName
    
    # Send alert (customize for your notification method)
    # Example: Send-MailMessage or Slack webhook
}
```

Create scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Services\clinic_cancellation_chatbot\scripts\health_check.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At 12:00am -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ClinicChatbot-HealthCheck" -Description "Monitors Clinic Cancellation Chatbot service"
```

---

## 🐛 Troubleshooting

### Service Won't Start

1. **Check logs:**
   ```powershell
   Get-Content data\logs\service-stderr.log -Tail 50
   ```

2. **Test manually:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python run.py
   ```

3. **Verify Python path:**
   ```powershell
   .\.venv\Scripts\python.exe --version
   ```

4. **Check .env file:**
   ```powershell
   Test-Path .env.production
   ```

### Database Connection Errors

```powershell
# Test connection
python -c "from app.infra.db import check_db_connection; check_db_connection()"

# Verify DATABASE_URL in .env.production
# Check PostgreSQL server is accessible from server
Test-NetConnection -ComputerName 192.168.1.220 -Port 5432
```

### Permission Errors

```powershell
# Grant service account permissions
icacls C:\Services\clinic_cancellation_chatbot /grant "SERVICE_ACCOUNT:(OI)(CI)F" /T
```

---

## 📝 Maintenance Schedule

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor message delivery rates

### Weekly
- [ ] Review application logs
- [ ] Check database size/performance
- [ ] Verify backups are running

### Monthly
- [ ] Update dependencies (`pip list --outdated`)
- [ ] Review and rotate logs
- [ ] Check disk space
- [ ] Review security patches

---

## 🆘 Emergency Procedures

### Service Crashed

```powershell
# Restart service
nssm restart ClinicCancellationChatbot

# If restart fails, check logs and manually start
nssm stop ClinicCancellationChatbot
python run.py  # Test manually
nssm start ClinicCancellationChatbot
```

### Rollback to Previous Version

```powershell
# Stop service
nssm stop ClinicCancellationChatbot

# Rollback Git
git log --oneline -10  # Find commit hash
git checkout <previous-commit-hash>

# Start service
nssm start ClinicCancellationChatbot
```

### Complete Service Reinstall

```powershell
# Remove service
nssm stop ClinicCancellationChatbot
nssm remove ClinicCancellationChatbot confirm

# Reinstall
.\scripts\install_service.ps1
nssm start ClinicCancellationChatbot
```

---

## 📞 Support Contacts

**Service Owner:** Jonathan Ives  
**IT Support:** TPCCC IT Team  
**Emergency Contact:** [Phone/Email]

---

**Last Updated:** October 31, 2025  
**Version:** 1.0
