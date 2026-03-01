# URE MVP Deployment Status Check Script

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "           URE MVP DEPLOYMENT STATUS CHECK" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# 1. Check Lambda Function
Write-Host "1. Lambda Function Status" -ForegroundColor Yellow
Write-Host "   Checking ure-mvp-handler..." -NoNewline
try {
    $lambda = aws lambda get-function --function-name ure-mvp-handler --region us-east-1 --query 'Configuration.{Status:LastUpdateStatus,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout}' --output json | ConvertFrom-Json
    if ($lambda.Status -eq "Successful") {
        Write-Host " ✓ OK" -ForegroundColor Green
        Write-Host "      Runtime: $($lambda.Runtime), Memory: $($lambda.Memory)MB, Timeout: $($lambda.Timeout)s" -ForegroundColor Gray
    } else {
        Write-Host " ✗ FAILED" -ForegroundColor Red
        Write-Host "      Status: $($lambda.Status)" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host " ✗ NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

# 2. Check Lambda Layer
Write-Host "`n2. Lambda Layer" -ForegroundColor Yellow
Write-Host "   Checking ure-dependencies layer..." -NoNewline
try {
    $layers = aws lambda get-function --function-name ure-mvp-handler --region us-east-1 --query 'Configuration.Layers[*].Arn' --output json | ConvertFrom-Json
    if ($layers -and $layers.Count -gt 0) {
        Write-Host " ✓ OK" -ForegroundColor Green
        Write-Host "      Layer: $($layers[0])" -ForegroundColor Gray
    } else {
        Write-Host " ✗ NO LAYER ATTACHED" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host " ✗ ERROR" -ForegroundColor Red
    $allGood = $false
}

# 3. Check API Gateway
Write-Host "`n3. API Gateway" -ForegroundColor Yellow
Write-Host "   Checking ure-mvp-api..." -NoNewline
try {
    $api = aws apigateway get-rest-apis --region us-east-1 --query "items[?name=='ure-mvp-api'].{Id:id,Name:name}" --output json | ConvertFrom-Json
    if ($api) {
        Write-Host " ✓ OK" -ForegroundColor Green
        Write-Host "      API ID: $($api.Id)" -ForegroundColor Gray
        Write-Host "      Endpoint: https://$($api.Id).execute-api.us-east-1.amazonaws.com/dev/query" -ForegroundColor Gray
        $apiUrl = "https://$($api.Id).execute-api.us-east-1.amazonaws.com/dev/query"
    } else {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host " ✗ ERROR" -ForegroundColor Red
    $allGood = $false
}

# 4. Check DynamoDB Tables
Write-Host "`n4. DynamoDB Tables" -ForegroundColor Yellow
$tables = @("ure-conversations", "ure-user-profiles", "ure-village-amenities")
foreach ($table in $tables) {
    Write-Host "   Checking $table..." -NoNewline
    try {
        $status = aws dynamodb describe-table --table-name $table --region us-east-1 --query 'Table.TableStatus' --output text 2>&1
        if ($status -eq "ACTIVE") {
            Write-Host " ✓ OK" -ForegroundColor Green
        } else {
            Write-Host " ✗ $status" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }
}

# 5. Check IAM Role
Write-Host "`n5. IAM Role" -ForegroundColor Yellow
Write-Host "   Checking ure-mvp-lambda-role..." -NoNewline
try {
    $role = aws iam get-role --role-name ure-mvp-lambda-role --query 'Role.RoleName' --output text 2>&1
    if ($role -eq "ure-mvp-lambda-role") {
        Write-Host " ✓ OK" -ForegroundColor Green
    } else {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host " ✗ NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

# 6. Test API Endpoint
if ($apiUrl) {
    Write-Host "`n6. API Endpoint Test" -ForegroundColor Yellow
    Write-Host "   Sending test query..." -NoNewline
    try {
        $body = @{
            query = "Hello, test query"
            user_id = "status_check_user"
            language = "en"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
        
        if ($response.agent_used) {
            Write-Host " ✓ OK" -ForegroundColor Green
            Write-Host "      Agent: $($response.agent_used)" -ForegroundColor Gray
            Write-Host "      Response: $($response.response.Substring(0, [Math]::Min(80, $response.response.Length)))..." -ForegroundColor Gray
        } else {
            Write-Host " ✗ INVALID RESPONSE" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host " ✗ FAILED" -ForegroundColor Red
        Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
        $allGood = $false
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "                  ✓ ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
} else {
    Write-Host "                  ✗ SOME ISSUES DETECTED" -ForegroundColor Red
}
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($apiUrl) {
    Write-Host "API Endpoint: $apiUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Test with PowerShell:" -ForegroundColor Cyan
    Write-Host @"
`$body = @{
    query = "What crops are good for Maharashtra?"
    user_id = "test_user"
    language = "en"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$apiUrl" -Method POST -Body `$body -ContentType "application/json"
"@ -ForegroundColor White
    Write-Host ""
    Write-Host "Or open test_api.html in your browser for a web interface." -ForegroundColor Cyan
}

Write-Host ""
