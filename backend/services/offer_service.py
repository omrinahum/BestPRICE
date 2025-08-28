from sqlalchemy import select, func, desc, asc, and_, nulls_last, nulls_first
from backend.models.offers import Offer
from backend.models.search_offer_link import SearchOfferLink
from backend.schemas.offer_schema import OfferResponse
from backend.utils.error import NotFoundError, ValidationError

async def get_offers_for_search(search_id: int, session, page: int = 1, page_size: int = 20,
                                sort_by: str = "last_price", sort_order: str = "asc", filters: dict = None):
    """
    Fetch offers for a specific search ID with pagination.
    """
    # Page validation
    if page < 1 or page_size < 1 or page_size > 100:
        raise ValidationError("Invalid pagination parameters, must be positive integers and page_size <= 100.")

    # Calculate offset for pagination
    offset = (page - 1) * page_size
    
    # Build the base query
    base_query = (
        select(Offer)
        .join(SearchOfferLink, Offer.id == SearchOfferLink.offer_id)
        .where(SearchOfferLink.search_id == search_id)
    )
    
    # Apply filters at the database level
    filter_conditions = []
    if filters:
        if "price" in filters and filters["price"]:
            min_price, max_price = filters["price"]
            if min_price is not None:
                filter_conditions.append(Offer.last_price >= min_price)
            if max_price is not None:
                filter_conditions.append(Offer.last_price <= max_price)
        
        if "source" in filters and filters["source"]:
            filter_conditions.append(Offer.source == filters["source"])
        
        if "min_rating" in filters and filters["min_rating"] is not None:
            filter_conditions.append(Offer.rating >= filters["min_rating"])
    
    # Apply all filter conditions
    if filter_conditions:
        base_query = base_query.where(and_(*filter_conditions))
    
    # Apply sorting at the database level with proper null handling
    if sort_by == "last_price":
        if sort_order == "desc":
            base_query = base_query.order_by(desc(Offer.last_price).nulls_last())
        else:
            base_query = base_query.order_by(asc(Offer.last_price).nulls_last())
    elif sort_by == "rating":
        if sort_order == "desc":
            # For rating DESC: highest ratings first, nulls last
            base_query = base_query.order_by(desc(Offer.rating).nulls_last())
        else:
            # For rating ASC: lowest ratings first, nulls last
            base_query = base_query.order_by(asc(Offer.rating).nulls_last())
    
    # Get total count (after filtering, before pagination)
    count_query = base_query.with_only_columns(func.count(Offer.id))
    total_count_result = await session.execute(count_query)
    total_count = total_count_result.scalar()
    
    # Apply pagination to the sorted and filtered query
    paginated_query = base_query.offset(offset).limit(page_size)
    result = await session.execute(paginated_query)
    offers = result.scalars().all()

    if not offers:
        return {
            "offers": [],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": 0
            }
        }
    
    # Convert to response models
    offer_responses = [OfferResponse.from_orm(o) for o in offers]
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size

    return {
        "offers": offer_responses,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages
        }
    }
















