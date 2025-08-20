# 🛒 Price Comparison Engine (eBay + BestBuy)

A lightweight **price comparison web application** that aggregates product data from multiple sources (eBay and BestBuy), normalizes results into a unified format, and provides a clean frontend for searching, filtering, and comparing items.  

Built as a **7-day student project** to demonstrate backend integration, data normalization, and full-stack development.

---

## 🚀 Features
- **Search across sources** – query eBay + BestBuy in parallel.
- **Unified schema** – normalize heterogeneous APIs into one consistent format.
- **Filtering & sorting** – by price, rating, category.
- **React frontend** – search bar, results table, quick categories.
- **Compare products** – select multiple items to view side-by-side.
- **Optional price history** – store price snapshots and visualize trends.
- **Dockerized** – run locally with Docker Compose.

---

## 🛠️ Tech Stack
**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) – lightweight Python web framework
- [httpx](https://www.python-httpx.org/) – async HTTP client
- [Pydantic](https://docs.pydantic.dev/) – data validation and models
- [SQLAlchemy](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/) – ORM & migrations
- MySQL – persistent database

**Frontend**
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) – fast React dev environment
- [TailwindCSS](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/) – styling & UI components
- (Optional) [Recharts](https://recharts.org/) / [Plotly](https://plotly.com/javascript/) – price history graphs

**Deployment & Tools**
- Docker & Docker Compose
- pytest (backend testing)
- dotenv for configuration

---

## 🗄️ Database Schema (MVP)

### `offers`
| Column            | Type              | Notes                                  |
|-------------------|------------------|----------------------------------------|
| id (PK)           | BIGINT AUTO      |                                        |
| source            | VARCHAR(16)      | `ebay` / `bestbuy`                     |
| source_offer_id   | VARCHAR(128)     | Unique per source                      |
| title             | VARCHAR(255)     |                                        |
| price             | DECIMAL(12,2)    |                                        |
| currency          | CHAR(3)          | e.g. `USD`                             |
| url               | TEXT             | link to product                        |
| image_url         | TEXT NULL        |                                        |
| rating            | DECIMAL(3,2)     | optional                               |
| shipping_cost     | DECIMAL(12,2)    | optional                               |
| brand             | VARCHAR(64)      | optional                               |
| category          | VARCHAR(32)      | optional                               |
| specs_json        | JSON NULL        | parsed specs (RAM/CPU/ANC…)            |
| last_seen_at      | DATETIME         | updated on search                      |
| created_at        | DATETIME         |                                        |
| updated_at        | DATETIME         |                                        |

### `price_history` (optional)
| Column         | Type           | Notes                  |
|----------------|---------------|-------------------------|
| id (PK)        | BIGINT AUTO   |                         |
| offer_id (FK)  | BIGINT        | references `offers.id`  |
| price          | DECIMAL(12,2) |                         |
| currency       | CHAR(3)       |                         |
| fetched_at     | DATETIME      | snapshot timestamp      |

---

## 🔗 API Endpoints

### `GET /api/search`
**Query Params**
- `q` (string): search term
- `category` (optional: `"laptop"|"headphones"|...`)
- `min_price`, `max_price` (optional)
- `page`, `page_size` (pagination)

**Flow**
1. Query both eBay + BestBuy in parallel.
2. Normalize results into a common schema.
3. Apply filters and sorting.
4. Upsert into `offers` table.
5. Return JSON to frontend.

### `GET /api/price-history/{offer_id}`
- Returns historical price data for a given product.

---

## 🎨 Frontend Pages

- **Search Page**: input box + quick category chips  
- **Results Table**: unified items with filters and sorting  
- **Compare Drawer**: side-by-side comparison of selected products  
- **(Optional)** Price History modal with graph  

---

## 🗂️ Project Structure
```bash
price-compare/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entrypoint
│   │   ├── routers/
│   │   │   └── search.py   # /api/search endpoint
│   │   ├── adapters/
│   │   │   ├── ebay.py
│   │   │   └── bestbuy.py
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic models
│   │   └── utils/          # normalization, caching
│   └── tests/
│       └── test_search.py
├── frontend/
│   ├── src/
│   │   ├── pages/SearchPage.tsx
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   └── CompareDrawer.tsx
├── docker-compose.yml
├── README.md
└── .env.example
```

---

## 🧩 Development Plan (7 Days)

**Day 1 – Setup**
- Initialize FastAPI project  
- Setup MySQL + Alembic migrations  
- Define `offers` schema  

**Day 2 – eBay Adapter**
- Implement eBay API calls  
- Normalize data → `NormalizedOffer`  

**Day 3 – BestBuy Adapter + /api/search**
- Implement BestBuy adapter  
- Merge results, filtering, sorting  
- Save offers in DB  

**Day 4 – React Frontend**
- Setup React + Tailwind  
- Build search bar + table  

**Day 5 – Filters & Compare**
- Add quick categories & filters  
- Implement compare drawer  

**Day 6 – Price History (Optional)**
- Store snapshots in `price_history`  
- Graph endpoint + frontend modal  

**Day 7 – Polish & Delivery**
- Dockerize (backend + DB)  
- Write tests (normalize + search flow)  
- Document architecture & screenshots  

---

## ⚠️ Known Limitations (MVP)
- Only two sources (eBay + BestBuy)  
- Specs parsing (RAM/CPU/ANC…) is limited and regex-based  
- Alerts/notifications not included in MVP  
- No authentication (public search only)  

---

## 📸 Demo Screenshots
*(add screenshots or GIFs of the UI once ready)*

---

## 🧑‍💻 Authors
Project developed by **[Your Names]** as a student team project.  
