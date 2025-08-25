from sqlalchemy import select
from backend.models.offers import Offer
from backend.models.search_offer_link import SearchOfferLink
from backend.schemas.offer_schema import OfferResponse
from backend.utils.error import NotFoundError, ValidationError

async def get_offers_for_search(search_id: int, session, page: int = 1, page_size: int = 20,
                                sort_by: str = "last_price", sort_order: str = "asc"):
    """
    Fetch offers for a specific search ID with pagination.
    """
    # Page validation
    if page < 1 or page_size < 1 or page_size > 100:
        raise ValidationError("Invalid pagination parameters, must be positive integers and page_size <= 100.")

    # Calculate offset for pagination
    offset = (page - 1) * page_size
    
    # Build the sql query and execute
    query = (
        select(Offer)
        .join(SearchOfferLink, Offer.id == SearchOfferLink.offer_id)
        .where(SearchOfferLink.search_id == search_id)
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(query)
    offers = result.scalars().all()

    if not offers:
        return []

    # Sort offers based on the provided criteria, reverse is true if "desc" is provided
    reverse_bool = sort_order == "desc"
    if sort_by in { "last_price", "rating"}:
        offers.sort(key=lambda o: getattr(o, sort_by, None) or 0, reverse=reverse_bool)

    return [OfferResponse.from_orm(o) for o in offers]
















