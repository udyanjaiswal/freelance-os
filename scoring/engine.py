from urllib.parse import urlparse


def is_real_website(url):
    if not url:
        return False

    try:
        domain = urlparse(url).netloc.lower()

        excluded_domains = [
            "google.com",
            "goo.gl",
            "maps.app.goo.gl",
        ]

        return bool(domain) and not any(
            excluded in domain
            for excluded in excluded_domains
        )

    except Exception:
        return False


def get_score_breakdown(lead):
    score = 0
    breakdown = []

    # -------------------------
    # WEBSITE OPPORTUNITY
    # -------------------------

    if not is_real_website(lead.website):

        if lead.website:
            points = 35
            result = "Only map/profile link found"

        else:
            points = 45
            result = "No website found"

        score += points

        breakdown.append({
            "factor": "Website Opportunity",
            "result": result,
            "points": points,
        })

    else:

        points = 10
        score += points

        breakdown.append({
            "factor": "Website Opportunity",
            "result": "Business website already available",
            "points": points,
        })

    # -------------------------
    # CONTACTABILITY
    # -------------------------

    if lead.phone:

        score += 20

        breakdown.append({
            "factor": "Phone",
            "result": "Available",
            "points": 20,
        })

    if lead.email:

        score += 10

        breakdown.append({
            "factor": "Email",
            "result": "Available",
            "points": 10,
        })

    # -------------------------
    # BUSINESS QUALITY
    # -------------------------

    rating = getattr(lead, "rating", None)
    reviews = getattr(lead, "reviews", None)

    if rating is not None and reviews is not None:

        if rating >= 4.0 and reviews >= 20:

            score += 10

            breakdown.append({
                "factor": "Business Quality",
                "result": f"{rating}★ with {reviews} reviews",
                "points": 10,
            })

        elif rating >= 3.5 and reviews >= 10:

            score += 5

            breakdown.append({
                "factor": "Business Quality",
                "result": f"{rating}★ with {reviews} reviews",
                "points": 5,
            })

    # -------------------------
    # BUSINESS INFORMATION
    # -------------------------

    if lead.business_name and lead.category:

        score += 5

        breakdown.append({
            "factor": "Business Information",
            "result": "Business and category identified",
            "points": 5,
        })

    # -------------------------
    # PRIORITY
    # -------------------------

    score = min(score, 100)

    return score, breakdown


def score_lead(lead):
    score, breakdown = get_score_breakdown(lead)

    if score >= 65:
        potential = "high"

    elif score >= 40:
        potential = "medium"

    else:
        potential = "low"

    lead.score = score
    lead.potential = potential

    lead.save(
        update_fields=[
            "score",
            "potential",
            "updated_at",
        ]
    )

    return score, potential, breakdown 