# BestPRICE - Price Comparison API

Price comparison platform with real-time data aggregation from Amazon, Ebay and more. Features async processing, intelligent caching, and comprehensive API integration.

## Key Features

- **Multi-Source Aggregation**: Parallel API calls to eBay, Amazon, and DummyJSON
- **Intelligent Caching**: OAuth2 token caching with automatic refresh (2-hour expiry)
- **Async Processing**: Non-blocking I/O operations for optimal performance
- **Advanced Filtering**: Price range, source, and rating-based filtering
- **Price History Tracking**: Historical price data with trend analysis and visualization
- **Automated Price Polling**: Daily background tasks to track watchlist item prices
- **User Watchlists**: Track and monitor specific items with price alerts
- **Cross-Platform Compatibility**: Windows, Linux, macOS support

## Architecture Highlights

- **Clean Architecture**: Separation of concerns with adapters, services, and repositories
- **Database Abstraction**: SQLAlchemy ORM with async support
- **Background Task Scheduling**: APScheduler for automated price tracking
- **API Rate Limiting**: Respectful external API usage with request throttling
- **Type Safety**: Pydantic models for data validation
- **Comprehensive Testing**: Unit, integration, and adapter tests

## Project Structure

```
BestPRICE/
├── backend/
│   ├── adapters/           # External API integrations
│   │   ├── ebay_adapter.py
│   │   ├── amazon_adapter.py
│   │   └── dummyjson_adapter.py
│   ├── models/             # Database models
│   │   ├── offers.py
│   │   ├── pricehistory.py
│   │   └── users.py
│   ├── routers/            # API endpoints
│   │   ├── search_router.py
│   │   ├── offer_router.py
│   │   └── user_router.py
│   ├── services/           # Business logic
│   │   ├── offer_service.py
│   │   ├── pricehistory_service.py
│   │   └── data_transformation_service.py
│   ├── tasks/              # Background tasks
│   │   └── price_tracker.py
│   ├── repositories/       # Data access layer
│   ├── utils/              # Helper functions
│   ├── scheduler.py        # Task scheduler
│   └── main.py             # FastAPI application
├── scripts/                # Utility scripts
│   ├── generate_price_history.py
│   └── test_price_polling.py
├── tests/                  # Comprehensive test suite
│   ├── test_adapters/
│   ├── test_services/
│   ├── test_integration/
│   └── test_repository/
├── frontend/               # React frontend
│   └── src/
│       └── components/
│           └── PriceHistoryModal.jsx
└── requirements.txt
```

## Setup

**Prerequisites:** Python 3.8+, Node.js 18+, eBay API credentials

### Backend Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd BestPRICE

# 2. Create virtual environment
python -m venv venv

# 3.Activate virtual environment (Windows)
venv\Scripts\activate

# 4.Activate virtual environment (Linux/macOS)
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Initialize database
python backend.init_db.py
```

**Environment Configuration:**
Create `backend/.env`:
```env
# Database Configuration
DATABASE_URL=sqlite:///./bestprice.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./bestprice.db

# eBay API (Required)
EBAY_CLIENT_ID=your_ebay_client_id_here
EBAY_CLIENT_SECRET=your_ebay_client_secret_here

# Amazon API via RapidAPI (Optional)
AMAZON_API_KEY=your_rapidapi_key_here
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running

**Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## API Endpoints

**Search:**
- `POST /search/` - Create search
- `GET /search/recent` - Recent searches

**Offers:**
- `GET /offers?search_id={id}` - Get offers (supports filtering: min_price, max_price, source, min_rating)
- `GET /offers/price/{offer_id}` - Price history

**User:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /user/watchlist` - Get user watchlist
- `POST /user/watchlist` - Add item to watchlist
- `DELETE /user/watchlist/{offer_id}` - Remove from watchlist

**Health:**
- `GET /health` - Status check

## Testing

**Run All Tests:**
```bash
# Activate virtual environment first
pytest
```

**Test Categories:**
```bash
# Adapter tests (external API integration)
pytest tests/test_adapters/ -v

# Service layer tests
pytest tests/test_services/ -v

# Integration tests
pytest tests/test_integration/ -v

# Repository tests
pytest tests/test_repository/ -v

# Coverage report
pytest --cov=backend --cov-report=html
```

**Platform-Specific Test Scripts:**
```bash
# Windows
.\run_tests_windows.ps1

# Linux/macOS
./run_tests.sh
```

## Tech Stack

**Backend:**
- FastAPI (async web framework)
- SQLAlchemy (ORM with async support)
- APScheduler (background task scheduling)
- Pydantic (data validation)
- aiosqlite (async SQLite driver)
- httpx (async HTTP client)
- pytest (testing framework)

**Frontend:**
- React 18+
- Recharts (price visualization)
- Vite (build tool)
- Lucide React (icons)

**External APIs:**
- eBay Browse API (OAuth2)
- Amazon Product API (RapidAPI)
- DummyJSON (testing)
- More APIs can be added as needed

## Performance Features

- **Async Architecture**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Search Caching**: Reduces API calls overhead
- **Parallel Processing**: Concurrent external API calls
- **Database Indexing**: Optimized queries on price, source, date fields
- **Scheduled Background Tasks**: Automated price updates with minimal overhead

## Price History & Tracking

### Automated Price Polling

The system includes automated price tracking for watchlist items. A background scheduler polls external APIs daily to update price history.

**Configuration:**
- Runs daily at 2:00 AM
- Tracks only watchlist items (efficient resource usage)

**Manual Testing:**
```bash
python scripts/test_price_polling.py
```

### Generating Historical Data

For demonstration purposes, synthetic historical price data can be generated for watchlist items.

**Generate 60 days of price history:**
```bash
python scripts/generate_price_history.py
```

### Price History Visualization

The frontend includes interactive price history graphs powered by Recharts

**Access:** Click the history button on any watchlist item to view the price trend graph.


