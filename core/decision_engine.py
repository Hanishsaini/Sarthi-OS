def optimize_itinerary(context, places):
    """
    places: list of dicts with keys: name, type, best_time, notes, tags (optional)
    Returns top 3 places sorted by score.
    """
    max_places = 3
    tourist_type = context.get("tourist_type", "general")
    budget = context.get("budget", "medium")

    # Scoring weights
    weights = {
        "relevance": 0.5,
        "type_match": 0.3,
        "budget_match": 0.2
    }

    # Define type-based keyword preferences
    type_prefs = {
        "couple": ["romantic", "scenic", "sunset", "garden", "lake"],
        "family": ["safe", "easy", "comfortable", "museum", "park"],
        "solo": ["exploration", "offbeat", "flexible", "cafe", "walk"],
        "general": []
    }

    # Budget preference keywords
    budget_prefs = {
        "low": ["free", "public", "street", "market"],
        "medium": [],
        "high": ["palace", "heritage", "luxury", "private"]
    }

    scored_places = []
    for place in places:
        # Assume place is a dict with at least 'name'
        name = place.get("name", "").lower()
        tags = place.get("tags", []) if isinstance(place.get("tags"), list) else []

        # Relevance score (default 1)
        relevance = 1.0

        # Type match score
        type_score = 0.0
        prefs = type_prefs.get(tourist_type, [])
        for kw in prefs:
            if kw in name or any(kw in tag.lower() for tag in tags):
                type_score += 0.25
        type_score = min(type_score, 1.0)   # cap at 1

        # Budget match score
        budget_score = 0.0
        prefs_b = budget_prefs.get(budget, [])
        for kw in prefs_b:
            if kw in name or any(kw in tag.lower() for tag in tags):
                budget_score += 0.5
        budget_score = min(budget_score, 1.0)

        # Total score
        total = (weights["relevance"] * relevance +
                 weights["type_match"] * type_score +
                 weights["budget_match"] * budget_score)
        scored_places.append((total, place))

    # Sort descending and take top max_places
    scored_places.sort(key=lambda x: x[0], reverse=True)
    selected = [place for _, place in scored_places[:max_places]]
    return selected