def optimize_itinerary(context, places):
    """
    Convert raw place list → optimized itinerary
    """

    max_places = 4

    # Priority filtering based on tourist type
    if context["tourist_type"] == "couple":
        priority_places = [p for p in places if "sunset" in p or "view" in p or "romantic" in p]

    elif context["tourist_type"] == "family":
        priority_places = [p for p in places if "safe" in p or "easy" in p or "comfortable" in p]

    else:
        priority_places = places

    # Limit places strictly
    selected = priority_places[:max_places]

    return selected