import os
import requests


FOURSQUARE_URL = "https://places-api.foursquare.com/places/search"


def search_foursquare(query, city, limit=20):
    api_key = os.getenv("FOURSQUARE_API_KEY")

    if not api_key:
        print("Foursquare API key not configured.")
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "X-Places-Api-Version": "2025-06-17",
    }

    params = {
        "query": query,
        "near": city,
        "limit": min(limit, 50),
        "fields": (
            "fsq_place_id,"
            "name,"
            "categories,"
            "location,"
            "tel,"
            "website,"
            "email"
        ),
    }

    try:
        response = requests.get(
            FOURSQUARE_URL,
            headers=headers,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:
        print(f"Foursquare error: {error}")
        return []

    places = data.get("results", [])

    leads = []

    for place in places:
        location = place.get("location", {})
        categories = place.get("categories", [])

        category = query

        if categories:
            category = categories[0].get("name", query)

        address_parts = [
            location.get("address"),
            location.get("locality"),
            location.get("postcode"),
        ]

        address = ", ".join(
            part for part in address_parts if part
        )

        leads.append({
            "business_name": place.get("name", ""),
            "category": category,
            "address": address,
            "city": location.get("locality") or city,
            "phone": place.get("tel", ""),
            "email": place.get("email", ""),
            "website": place.get("website", ""),
            "source": "foursquare",
            "source_id": place.get("fsq_place_id", ""),
        })

    print(f"Foursquare returned {len(leads)} places.")

    return leads