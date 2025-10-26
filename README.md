# BestPRICE

A price comparison platform that aggregates product data from multiple sources (eBay, Amazon) with price history tracking and automated monitoring.

## Features

- Multi-source product search (eBay, Amazon, DummyJSON)
- Price history tracking with interactive graphs
- User watchlists with automated daily price updates
- OAuth2 token caching for eBay API
- Async processing for better performance
- Price filtering and sorting

## Tech Stack

**Backend:**
- FastAPI + SQLAlchemy (async)
- APScheduler for background tasks
- SQLite with aiosqlite

**Frontend:**
- React + Vite
- Recharts for price graphs

**APIs:**
- eBay Browse API
- Amazon Product API (RapidAPI)

## Project Structure

```
BestPRICE/
├── backend/
│   ├── adapters/          # API integrations (eBay, Amazon, etc.)
│   ├── models/            # Database models
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── tasks/             # Background jobs
│   ├── repositories/      # Data access layer
│   └── scheduler.py       # Task scheduling
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── frontend/              # React app
```

## Setup & Running

**Prerequisites:** Python 3.8+, Node.js 18+, eBay API credentials

### 1. Clone and Navigate
```bash
git clone https://github.com/omrinahum/BestPRICE
cd BestPRICE
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate              # Windows
source venv/bin/activate           # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Initialize database
python backend/init_db.py
```

Create `backend/.env` with your API credentials:
```env
DATABASE_URL=sqlite:///./bestprice.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./bestprice.db

EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret
AMAZON_API_KEY=your_rapidapi_key  # Optional
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Run the Application

**Start Backend** (from project root):
```bash
# Make sure venv is activated
uvicorn backend.main:app --reload --port 8000
```

**Start Frontend** (new terminal):
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

**Search**
- `POST /search/` - Create new search
- `GET /search/recent` - Get recent searches

**Offers**
- `GET /offers?search_id={id}` - Get offers (supports min_price, max_price, source filters)
- `GET /offers/price/{offer_id}` - Get price history

**User**
- `POST /auth/register` - Register
- `POST /auth/login` - Login
- `GET /user/watchlist` - Get watchlist
- `POST /user/watchlist` - Add to watchlist
- `DELETE /user/watchlist/{offer_id}` - Remove from watchlist

## Testing

Run all tests:
```bash
.\scripts\run_tests_windows.ps1  # Windows
./scripts/run_tests.sh           # Linux/macOS
```

Or use pytest directly:
```bash
pytest                           # All tests
pytest tests/test_adapters/ -v   # Adapter tests only
pytest tests/test_services/ -v   # Service tests only
```

## Price History & Tracking

The app tracks price changes over time for watchlist items.

**Automated Updates:**
- Background task runs daily at 2:00 AM
- Only polls prices for items in user watchlists
- Test manually: `python scripts/test_price_polling.py`

**Demo Data:**
Generate 60 days of synthetic price history:
```bash
python scripts/generate_price_history.py
```

**Viewing History:**
Click the history button on any watchlist item to see the price trend graph.

## Architecture Notes

- Clean separation: adapters → services → repositories → models
- Async/await throughout for better concurrency
- OAuth2 tokens cached with 2-hour expiry
- Database queries optimized with indexes on price, source, and date fields
- Background scheduler runs in FastAPI lifespan context
