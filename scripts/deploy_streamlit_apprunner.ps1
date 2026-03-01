# Deploy Streamlit UI to AWS App Runner

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     URE MVP - Deploy Streamlit UI to AWS App Runner" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Configuration
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = "188238313375"
$ECR_REPO_NAME = "ure-streamlit-ui"
$APP_RUNNER_SERVICE_NAME = "ure-streamlit-service"
$API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  AWS Region: $AWS_REGION"
Write-Host "  ECR Repository: $ECR_REPO_NAME"
Write-Host "  App Runner Service: $APP_RUNNER_SERVICE_NAME"
Write-Host "  API Endpoint: $API_ENDPOINT"
Write-Host ""

# Step 1: Create ECR Repository
Write-Host "Step 1: Creating ECR Repository..." -ForegroundColor Cyan
try {
    $ecrRepo = aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ ECR repository already exists" -ForegroundColor Green
    }
} catch {
    Write-Host "  Creating new ECR repository..." -ForegroundColor Gray
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION | Out-Null
    Write-Host "  ✓ ECR repository created" -ForegroundColor Green
}

$ECR_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
Write-Host "  ECR URI: $ECR_URI" -ForegroundColor Gray
Write-Host ""

# Step 2: Login to ECR
Write-Host "Step 2: Logging in to ECR..." -ForegroundColor Cyan
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Logged in to ECR" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to login to ECR" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Build Docker Image
Write-Host "Step 3: Building Docker image..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
docker build -t $ECR_REPO_NAME .
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to build Docker image" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Tag Image
Write-Host "Step 4: Tagging Docker image..." -ForegroundColor Cyan
docker tag "${ECR_REPO_NAME}:latest" "${ECR_URI}:latest"
Write-Host "  ✓ Image tagged" -ForegroundColor Green
Write-Host ""

# Step 5: Push to ECR
Write-Host "Step 5: Pushing image to ECR..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
docker push "${ECR_URI}:latest"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Image pushed to ECR" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to push image" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Create App Runner Service
Write-Host "Step 6: Creating App Runner service..." -ForegroundColor Cyan

# Create service configuration JSON
$serviceConfig = @{
    ServiceName = $APP_RUNNER_SERVICE_NAME
    SourceConfiguration = @{
        ImageRepository = @{
            ImageIdentifier = "${ECR_URI}:latest"
            ImageRepositoryType = "ECR"
            ImageConfiguration = @{
                Port = "8501"
                RuntimeEnvironmentVariables = @{
                    USE_API_MODE = "true"
                    API_ENDPOINT = $API_ENDPOINT
                }
            }
        }
        AutoDeploymentsEnabled = $true
    }
    InstanceConfiguration = @{
        Cpu = "1 vCPU"
        Memory = "2 GB"
    }
    HealthCheckConfiguration = @{
        Protocol = "HTTP"
        Path = "/_stcore/health"
        Interval = 10
        Timeout = 5
        HealthyThreshold = 1
        UnhealthyThreshold = 5
    }
} | ConvertTo-Json -Depth 10

# Save to temp file
$serviceConfig | Out-File -FilePath "temp_apprunner_config.json" -Encoding utf8

try {
    # Check if service exists
    $existingService = aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[?ServiceName=='$APP_RUNNER_SERVICE_NAME'].ServiceArn" --output text 2>&1
    
    if ($existingService -and $existingService -ne "") {
        Write-Host "  Service already exists, updating..." -ForegroundColor Yellow
        aws apprunner update-service --service-arn $existingService --source-configuration "ImageRepository={ImageIdentifier=${ECR_URI}:latest,ImageRepositoryType=ECR,ImageConfiguration={Port=8501,RuntimeEnvironmentVariables={USE_API_MODE=true,API_ENDPOINT=$API_ENDPOINT}}}" --region $AWS_REGION
        $serviceArn = $existingService
    } else {
        Write-Host "  Creating new service..." -ForegroundColor Gray
        $createResult = aws apprunner create-service --cli-input-json file://temp_apprunner_config.json --region $AWS_REGION | ConvertFrom-Json
        $serviceArn = $createResult.Service.ServiceArn
    }
    
    Write-Host "  ✓ App Runner service created/updated" -ForegroundColor Green
    Write-Host "  Service ARN: $serviceArn" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Failed to create App Runner service" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup temp file
    if (Test-Path "temp_apprunner_config.json") {
        Remove-Item "temp_apprunner_config.json"
    }
}
Write-Host ""

# Step 7: Wait for service to be ready
Write-Host "Step 7: Waiting for service to be ready..." -ForegroundColor Cyan
Write-Host "  This may take 3-5 minutes..." -ForegroundColor Gray

$maxAttempts = 30
$attempt = 0
$serviceUrl = ""

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 10
    $attempt++
    
    $serviceStatus = aws apprunner describe-service --service-arn $serviceArn --region $AWS_REGION --query 'Service.Status' --output text 2>&1
    
    Write-Host "  Attempt $attempt/$maxAttempts - Status: $serviceStatus" -ForegroundColor Gray
    
    if ($serviceStatus -eq "RUNNING") {
        $serviceUrl = aws apprunner describe-service --service-arn $serviceArn --region $AWS_REGION --query 'Service.ServiceUrl' --output text
        Write-Host "  ✓ Service is running!" -ForegroundColor Green
        break
    } elseif ($serviceStatus -eq "CREATE_FAILED" -or $serviceStatus -eq "UPDATE_FAILED") {
        Write-Host "  ✗ Service deployment failed" -ForegroundColor Red
        exit 1
    }
}

if ($serviceUrl -eq "") {
    Write-Host "  ⚠ Service is still deploying. Check AWS Console for status." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "                  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your Streamlit UI is now live at:" -ForegroundColor Yellow
    Write-Host "  https://$serviceUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "Opening in browser..." -ForegroundColor Gray
    Start-Process "https://$serviceUrl"
    Write-Host ""
    Write-Host "Service Details:" -ForegroundColor Cyan
    Write-Host "  Service Name: $APP_RUNNER_SERVICE_NAME" -ForegroundColor Gray
    Write-Host "  Service ARN: $serviceArn" -ForegroundColor Gray
    Write-Host "  Region: $AWS_REGION" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Cyan
    Write-Host "  aws apprunner list-operations --service-arn $serviceArn --region $AWS_REGION" -ForegroundColor White
    Write-Host ""
    Write-Host "To delete the service:" -ForegroundColor Cyan
    Write-Host "  aws apprunner delete-service --service-arn $serviceArn --region $AWS_REGION" -ForegroundColor White
    Write-Host ""
}
