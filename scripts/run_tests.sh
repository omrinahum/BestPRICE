#!/bin/bash
# Linux/macOS shell script to run tests with test DB isolation
# Change to project root directory
cd "$(dirname "$0")/.."

export DATABASE_URL="sqlite:///./test.db"
export ASYNC_DATABASE_URL="sqlite+aiosqlite:///./test.db"
pytest --maxfail=1 --disable-warnings --tb=short