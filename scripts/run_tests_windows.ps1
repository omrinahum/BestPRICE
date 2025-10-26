# PowerShell script to run tests with test DB isolation
# Change to project root directory
Set-Location $PSScriptRoot\..

$env:DATABASE_URL="sqlite:///./test.db"
$env:ASYNC_DATABASE_URL="sqlite+aiosqlite:///./test.db"
pytest --maxfail=1 --disable-warnings --tb=short