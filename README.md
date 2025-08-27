# BestPRICE - Price Comparison Application

A modern price comparison application that helps users find the best prices across multiple sources. Built with FastAPI backend and React frontend.

## 🚀 Features

- **Smart Search**: Search for products across multiple sources
- **Price Comparison**: Compare prices from different retailers
- **Price History**: Track price changes over time
- **Filtering & Sorting**: Advanced filtering by price range and sorting options
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live price tracking and updates

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React 19 with Vite
- **Database**: SQLite (can be easily switched to PostgreSQL/MySQL)
- **API**: RESTful API with automatic documentation

## 📁 Project Structure

```
BestPRICE/
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── adapters/           # External API adapters
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main app component
│   │   └── App.css         # Application styles
│   └── package.json        # Frontend dependencies
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd BestPRICE
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Initialize the database**:
```bash
cd backend
python init_db.py
```

### Frontend Setup

1. **Install Node.js dependencies**:
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Option 1: Run Both Servers (Recommended)

**Windows:**
```bash
.\run_app.ps1
```

**Unix/MacOS:**
```bash
./run_app.sh
```

### Option 2: Run Servers Separately

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Access URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### Search
- `POST /search/` - Create a new search
- `GET /search/recent` - Get recent searches

### Offers
- `GET /offers` - Get offers with filtering and pagination
- `GET /offers/price/{offer_id}` - Get price history for an offer

### Health
- `GET /health` - Health check endpoint

### Query Parameters for Offers

- `search_id` (required): ID of the search
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)
- `sort_by` (optional): Sort field - 'last_price' or 'created_at' (default: 'last_price')
- `sort_order` (optional): Sort order - 'asc' or 'desc' (default: 'asc')
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

## 🎨 Frontend Features

### Search Interface
- Clean, intuitive search form
- Real-time validation
- Loading states and error handling

### Offers Display
- Responsive grid layout
- Product images with fallbacks
- Price, seller, and rating information
- Source badges and external links

### Filtering & Sorting
- Price range filtering
- Sort by price or date
- Clear filters functionality
- Server-side processing for performance

### Price History
- Modal popup with detailed information
- Price change calculations
- Chronological history display
- Interactive charts (future enhancement)

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_services/test_offer_service.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend Deployment

1. **Production server setup**:
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Environment variables**:
```bash
export DATABASE_URL="postgresql://user:password@localhost/bestprice"
export SECRET_KEY="your-secret-key"
```

### Frontend Deployment

1. **Build for production**:
```bash
cd frontend
npm run build
```

2. **Serve static files**:
```bash
npm install -g serve
serve -s dist -l 3000
```

## 🔧 Configuration

### Backend Configuration

Create a `.env` file in the backend directory:
```env
DATABASE_URL=sqlite:///./bestprice.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Frontend Configuration

Update API base URL in `frontend/src/App.jsx` if needed:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce

## 🔮 Future Enhancements

- [ ] User authentication and profiles
- [ ] Price alerts and notifications
- [ ] Advanced analytics and charts
- [ ] Mobile app (React Native)
- [ ] Machine learning price predictions
- [ ] Integration with more retailers
- [ ] Social features and reviews
- [ ] Export functionality
- [ ] Dark mode theme
- [ ] Internationalization (i18n)

## 📊 Performance

- **Backend**: FastAPI provides excellent performance with async support
- **Frontend**: React 19 with optimized rendering
- **Database**: Efficient queries with proper indexing
- **Caching**: Redis integration for improved performance (future)

## 🔒 Security

- Input validation with Pydantic
- CORS configuration
- SQL injection protection
- XSS prevention
- Rate limiting (future enhancement)

---

**Built with ❤️ using FastAPI and React**


