# 🛒 Price Comparison Engine (eBay + BestBuy)

A lightweight **price comparison web application** that aggregates product data from multiple sources (eBay and BestBuy), normalizes results into a unified format, and provides a clean frontend for searching, filtering, and comparing items.

Built as a **7-day student project** to demonstrate backend integration, data normalization, and full-stack development.

---

## 🚀 Features
- **Search across sources** – query eBay + BestBuy in parallel.
- **Unified schema** – normalize heterogeneous APIs into one consistent format.
- **Filtering & sorting** – by price, rating, category.
- **Recent searches analytics** – see latest queries.
- **Price history** – store price snapshots and visualize trends.
- **React frontend** – search bar, results table, quick categories.
- **Compare products** – select multiple items to view side-by-side.

---

## 🛠️ Tech Stack
**Backend:** FastAPI, httpx, Pydantic, SQLAlchemy, Alembic, SQLite  
**Frontend:** React, Vite, TailwindCSS, shadcn/ui, Recharts/Plotly  
**Testing:** pytest, pytest-asyncio  
**Other:** Docker, dotenv

---

## 🔗 API Endpoints

### `POST /search`
Create a new search and return metadata.
- Request: `{ "query": "iphone", "filters": { "price": [100, 1000] } }`
- Response: `{ "id": 1, "query": "iphone", "filters": { "price": [100, 1000] }, "normalized_query": "iphone", "created_at": "..." }`

### `GET /search/recent?limit=10`
Get recent searches.
- Response: `[ { "id": 1, "query": "iphone", ... }, ... ]`

### `GET /offers?search_id=1&page=1&page_size=20&sort_by=last_price&sort_order=asc`
Get offers for a search, paginated and sorted.
- Response: `[ { "id": 101, "title": "Apple iPhone 13", "last_price": 899.99, ... }, ... ]`

### `GET /offers/{offer_id}`
Get price history for an offer.
- Response: `[ { "id": 1, "price": 899.99, "currency": "USD", "fetched_at": "..." }, ... ]`

---

## ⚠️ Error Handling

All endpoints return structured error responses:
- `404 Not Found`: `{ "detail": "No offers found for search_id 123" }`
- `422 Validation Error`: `{ "detail": "Invalid pagination parameters." }`
- `502 External API Error`: `{ "detail": "External service error: ..." }`
- `500 Internal Error`: `{ "detail": "Database error occurred. Please try again later." }`

---

## 🗂️ Project Structure
```bash
BestPRICE/
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── adapters/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── utils/
│   └── tests/
├── frontend/
│   └── src/
├── README.md
└── .env.example
```


