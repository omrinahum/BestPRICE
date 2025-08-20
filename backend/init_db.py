# backend/init_db.py
from .database import engine
from .models.offers import Offer
from .models.pricehistory import PriceHistory
from .models.searches import Search


def init_db():
    from backend.database import Base
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
