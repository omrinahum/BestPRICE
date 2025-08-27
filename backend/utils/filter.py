def apply_filters(items, filters):
    """
    Apply filters (price, condition, etc.) to a list of offer dicts or Pydantic models.
    """
    if not items:
        return items

    # Price filter
    price_rng = filters.get("price")
    if price_rng and len(price_rng) == 2:
        minp = float(price_rng[0] or 0)
        maxp = float(price_rng[1] or float("inf"))
        
        def get_price(item):
            # Support both dict and Pydantic model
            if hasattr(item, "last_price"):
                return float(item.last_price)
            
            return float(item.get("last_price", 0))
        
        items = [item for item in items if minp <= get_price(item) <= maxp]

    return items