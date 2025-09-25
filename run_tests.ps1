# Run tests using pytest
Write-Host "Running Autoshop Tests with pytest" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if in virtual environment or uv available
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Using uv to run pytest..." -ForegroundColor Green
    uv run pytest tests -v
} elseif ($env:VIRTUAL_ENV) {
    Write-Host "Using pytest from virtual environment..." -ForegroundColor Green
    pytest tests -v
} else {
    Write-Host "Using system pytest..." -ForegroundColor Yellow
    pytest tests -v
}

Write-Host "`nTest run completed." -ForegroundColor Green
Write-Host "`nFor more options, use:" -ForegroundColor Cyan
Write-Host "  pytest tests -m 'not integration' -v    # Skip integration tests" -ForegroundColor Gray
Write-Host "  pytest tests -m integration -v          # Only integration tests" -ForegroundColor Gray
Write-Host "  pytest tests/test_unit/ -v              # Test specific module" -ForegroundColor Gray
Write-Host "  pytest --collect-only                   # Show all available tests" -ForegroundColor Gray
