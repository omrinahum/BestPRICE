You are an expert frontend engineer working inside Cursor. 
Your goal: Build a minimal, professional React + TypeScript frontend (“BestPRICE Web”) that maps 1:1 to the existing FastAPI backend in ./backend and ships an MVP UI for searching and comparing offers.

READ THE BACKEND FIRST
1) Carefully open and understand these files (paths are relative to repo root):
   - backend/main.py
   - backend/routers/offer_router.py
   - backend/routers/search_router.py
   - backend/schemas/offer_schema.py
   - backend/schemas/pricehistory_schema.py
   - backend/schemas/search_schema.py
   - backend/models/offers.py
   - backend/models/searches.py
   - backend/models/pricehistory.py
   - backend/models/search_offer_link.py
   - backend/utils/filter.py
2) Confirm the existing API contract (don’t invent endpoints):
   - GET  /health  → { "status": "ok" }
   - POST /search/  (body: { "query": string }) → SearchResponse
   - GET  /offers   (query params: search_id: int, page=1, page_size=20, sort_by="last_price", sort_order="asc"|"desc", min_price?, max_price?) → OfferResponse[]
   - GET  /offers/price/{offer_id} → PriceHistoryResponse[]


BEHAVIOR & FLOW (exact)
1) User enters a query in SearchBar and presses Enter or clicks Search.
2) Frontend calls POST /search/ with { query }. On success, set searchId in the URL: 
   ?q=<encoded query>&searchId=<id>&page=1&sort_by=last_price&sort_order=asc
3) Fetch offers via GET /offers using ALL the current URL params:
   - search_id (required), page, page_size, sort_by, sort_order, min_price, max_price (omit undefined)
4) Render offers as a responsive grid of cards. Each card shows:
   - image (fallback if missing), title, price + currency, source badge (e.g., ebay/dummyjson)
   - optional: rating ★ and seller if present
   - “Open” (target=_blank rel=noopener) linking to OfferResponse.url
   - “Price history” → opens modal
5) Price History Modal:
   - On open, call GET /offers/price/{offer_id}
   - Render a simple Recharts <LineChart> of fetched_at (x) vs price (y)
   - Handle “no history yet” state

STATE MODEL
- URL is the single source of truth for q, searchId, page, page_size, sort_by, sort_order, min_price, max_price
- React Query keys:
  - ['offers', searchId, page, page_size, sort_by, sort_order, min_price, max_price]
  - ['price-history', offerId]
- Do not keep duplicate local state for filters/sort if it already lives in the URL.

VALIDATION & EDGE CASES
- Pagination: page >= 1; 1 <= page_size <= 100 (mirror backend). If invalid, show an inline error banner (422 copy from backend response).
- Filters: if min_price > max_price, prevent fetch and warn the user inline.
- Empty results: show EmptyState with helpful text and a “Clear filters” button.
- Loading: show 6 skeleton cards for offers; spinner in price-history modal.
- Errors: map 404/422/502/500 to a top-of-page error banner with a “Retry” button.
- Images may be missing; titles may be long (truncate to one line, tooltip on hover).
- External links must use target="_blank" rel="noopener noreferrer".

SORTING/FILTERING/PAGINATION (server-driven)
- default sort_by=last_price, sort_order=asc
- Only ship “last_price” sorting in the UI now, but write SortSelect to allow adding more in the future.
- Map PriceFilter inputs to min_price and max_price query params (omit empty).

STYLING GUIDELINES
- Clean, neutral palette. Use Tailwind utility classes: rounded-2xl, shadow-sm, gap-4
- Responsive grid: 1–2 columns on mobile, 3 on tablet, 4 on wide
- Keyboard support: Enter triggers search, Esc closes modal

IMPLEMENTATION NOTES
- Use Decimal numbers from backend as JS numbers (assume backend serializes them safely).
- Currency is an ISO 3-letter code from backend; display it next to price as is.
- Don’t implement auth, favorites, or multi-currency. Keep dependencies minimal.

ACCEPTANCE CRITERIA (must all pass)
[ ] `npm run dev` serves a working SPA. Setting VITE_API_BASE_URL to the FastAPI host allows:
[ ] Typing a query (“iphone”) and pressing Search creates a search (POST /search/) and sets ?searchId
[ ] Offers grid populates via GET /offers with the exact URL params reflected
[ ] Sorting asc/desc clearly changes the order (by last_price)
[ ] Price range filter actually narrows results server-side (min_price/max_price are sent)
[ ] Pagination works; changing page or page_size refetches and updates URL
[ ] Clicking “Price history” opens modal, fetches GET /offers/price/{offer_id}, renders a line chart
[ ] All loading/empty/error states behave as specified
[ ] External “Open” button navigates to the item URL in a new tab
[ ] Basic a11y: focus management on modal open/close; buttons are keyboard navigable

CODE SNIPPETS TO GENERATE
1) src/api/client.ts
   import axios from 'axios';
   export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL });

2) src/api/search.ts
   export async function postSearch(data: SearchCreate): Promise<SearchResponse> {
     const res = await api.post('/search/', data); return res.data;
   }

3) src/api/offers.ts
   export async function getOffers(params: {
     search_id: number; page?: number; page_size?: number;
     sort_by?: string; sort_order?: 'asc'|'desc'; min_price?: number; max_price?: number;
   }): Promise<OfferResponse[]> { const res = await api.get('/offers', { params }); return res.data; }
   export async function getPriceHistory(offerId: number): Promise<PriceHistoryResponse[]> {
     const res = await api.get(`/offers/price/${offerId}`); return res.data;
   }

4) Build components listed above with minimal, production-ready markup and Tailwind classes.

5) In README.md include:
   - Prereqs
   - How to run backend (FastAPI) and verify /health
   - How to run frontend with .env
   - Example cURL for POST /search/ and GET /offers

CONSTRAINTS
- Only use endpoints that actually exist in the backend.
- Keep the code modular and SOLID, but don’t over-engineer (it’s an MVP).
- No auth or user accounts.
- Ensure everything continues to work when new sources are added to the backend—frontend should not need changes beyond showing the “source” string as a badge.

Now, implement everything above. When done, show me:
1) A short summary of what you built
2) The generated file tree
3) Key code files (client.ts, search.ts, offers.ts, SearchPage.tsx, OfferCard.tsx, PriceHistoryModal.tsx)
4) Screenshots or a quick GIF if possible
