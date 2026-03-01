# URE MVP API Test Examples
# Run these commands in PowerShell to test the deployed API

$API_URL = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

Write-Host "`n=== URE MVP API Test Examples ===" -ForegroundColor Cyan
Write-Host "API Endpoint: $API_URL`n" -ForegroundColor Yellow

# Example 1: General Farming Query
Write-Host "Example 1: General Farming Query" -ForegroundColor Green
Write-Host "--------------------------------" -ForegroundColor Gray
$body1 = @{
    query = "What are the best crops for Maharashtra?"
    user_id = "farmer_001"
    language = "en"
} | ConvertTo-Json

Write-Host "Query: What are the best crops for Maharashtra?" -ForegroundColor White
Write-Host "Running..." -ForegroundColor Gray
$response1 = Invoke-RestMethod -Uri $API_URL -Method POST -Body $body1 -ContentType "application/json"
Write-Host "Agent Used: $($response1.agent_used)" -ForegroundColor Cyan
Write-Host "Response: $($response1.response.Substring(0, [Math]::Min(200, $response1.response.Length)))...`n" -ForegroundColor White

# Example 2: Government Scheme Query
Write-Host "`nExample 2: Government Scheme Query" -ForegroundColor Green
Write-Host "-----------------------------------" -ForegroundColor Gray
$body2 = @{
    query = "Tell me about PM-KISAN scheme"
    user_id = "farmer_002"
    language = "en"
} | ConvertTo-Json

Write-Host "Query: Tell me about PM-KISAN scheme" -ForegroundColor White
Write-Host "Running..." -ForegroundColor Gray
$response2 = Invoke-RestMethod -Uri $API_URL -Method POST -Body $body2 -ContentType "application/json"
Write-Host "Agent Used: $($response2.agent_used)" -ForegroundColor Cyan
Write-Host "Response: $($response2.response.Substring(0, [Math]::Min(200, $response2.response.Length)))...`n" -ForegroundColor White

# Example 3: Irrigation Query
Write-Host "`nExample 3: Irrigation Query" -ForegroundColor Green
Write-Host "---------------------------" -ForegroundColor Gray
$body3 = @{
    query = "How should I manage irrigation for my crops?"
    user_id = "farmer_003"
    language = "en"
} | ConvertTo-Json

Write-Host "Query: How should I manage irrigation for my crops?" -ForegroundColor White
Write-Host "Running..." -ForegroundColor Gray
$response3 = Invoke-RestMethod -Uri $API_URL -Method POST -Body $body3 -ContentType "application/json"
Write-Host "Agent Used: $($response3.agent_used)" -ForegroundColor Cyan
Write-Host "Response: $($response3.response.Substring(0, [Math]::Min(200, $response3.response.Length)))...`n" -ForegroundColor White

# Example 4: Hindi Language Query
Write-Host "`nExample 4: Hindi Language Query" -ForegroundColor Green
Write-Host "-------------------------------" -ForegroundColor Gray
$body4 = @{
    query = "मुझे खेती के बारे में मदद चाहिए"
    user_id = "farmer_004"
    language = "hi"
} | ConvertTo-Json

Write-Host "Query: मुझे खेती के बारे में मदद चाहिए (I need help with farming)" -ForegroundColor White
Write-Host "Running..." -ForegroundColor Gray
$response4 = Invoke-RestMethod -Uri $API_URL -Method POST -Body $body4 -ContentType "application/json"
Write-Host "Agent Used: $($response4.agent_used)" -ForegroundColor Cyan
Write-Host "Response: $($response4.response.Substring(0, [Math]::Min(200, $response4.response.Length)))...`n" -ForegroundColor White

Write-Host "`n=== All Examples Completed ===" -ForegroundColor Cyan
Write-Host "`nYou can modify these examples or create your own queries!" -ForegroundColor Yellow
Write-Host "`nBasic template:" -ForegroundColor Cyan
Write-Host @"
`$body = @{
    query = "Your question here"
    user_id = "your_user_id"
    language = "en"  # or "hi" for Hindi, "mr" for Marathi
} | ConvertTo-Json

Invoke-RestMethod -Uri "$API_URL" -Method POST -Body `$body -ContentType "application/json"
"@ -ForegroundColor White
