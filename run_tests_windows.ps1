#!/bin/bash
$env:DATABASE_URL="sqlite:///./test.db"
$env:ASYNC_DATABASE_URL="sqlite+aiosqlite:///./test.db"
pytest