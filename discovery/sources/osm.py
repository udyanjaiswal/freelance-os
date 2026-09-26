import re
import requests


def sanitize_osm_input(val):
    """Sanitize inputs to prevent Overpass QL grammar/regex injection."""
    if not val:
        return ""
    return re.sub(r'["\\;\[\]{}|\r\n\t]', '', str(val)).strip()


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


CATEGORY_TAGS = {
    "salon": [
        ("shop", "beauty"),
        ("shop", "hairdresser"),
    ],

    "salons": [
        ("shop", "beauty"),
        ("shop", "hairdresser"),
    ],

    "hair salon": [
        ("shop", "hairdresser"),
    ],

    "hair salons": [
        ("shop", "hairdresser"),
    ],

    "beauty salon": [
        ("shop", "beauty"),
    ],

    "beauty salons": [
        ("shop", "beauty"),
    ],

    "restaurant": [
        ("amenity", "restaurant"),
    ],

    "restaurants": [
        ("amenity", "restaurant"),
    ],

    "cafe": [
        ("amenity", "cafe"),
    ],

    "cafes": [
        ("amenity", "cafe"),
    ],

    "dentist": [
        ("amenity", "dentist"),
    ],

    "dentists": [
        ("amenity", "dentist"),
    ],

    "gym": [
        ("leisure", "fitness_centre"),
    ],

    "gyms": [
        ("leisure", "fitness_centre"),
    ],
}


def search_osm(query, city, limit=100):

    safe_query = sanitize_osm_input(query).lower()
    safe_city = sanitize_osm_input(city)

    if not safe_query or not safe_city:
        return []

    category_tags = CATEGORY_TAGS.get(safe_query)

    # Known category
    if category_tags:

        tag_queries = []

        for key, value in category_tags:

            tag_queries.append(
                f'nwr(area.searchArea)["{key}"="{value}"];'
            )

        query_body = "\n".join(tag_queries)

    # Unknown search term
    else:

        # Search business names instead of trying
        # to treat the search as a key=value tag.
        query_body = (
            f'nwr(area.searchArea)'
            f'[name~"{safe_query}",i];'
        )

    overpass_query = f"""
[out:json][timeout:90];

area["name"="{safe_city}"]->.searchArea;

(
    {query_body}
);

out tags;
"""

    headers = {
        "User-Agent": "FreelancerOS/1.0"
    }

    last_error = None

    for url in OVERPASS_URLS:

        try:

            print(f"Searching OSM for: {query} in {city}")
            print(f"Using Overpass: {url}")

            response = requests.post(
                url,
                data={
                    "data": overpass_query
                },
                headers=headers,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            print(
                f"OSM returned "
                f"{len(data.get('elements', []))} elements"
            )

            return parse_results(
                data,
                query,
                city,
                limit
            )

        except requests.RequestException as error:

            print(f"OSM provider failed: {error}")

            last_error = error

    raise Exception(
        f"All OSM providers failed: {last_error}"
    )


def parse_results(data, query, city, limit):

    results = []
    seen = set()

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        name = tags.get("name")

        if not name:
            continue

        source_id = (
            f"{element.get('type')}_"
            f"{element.get('id')}"
        )

        if source_id in seen:
            continue

        seen.add(source_id)

        results.append({
            "business_name": name,

            "category": query,

            "address": build_address(tags),

            "city": city,

            "phone": (
                tags.get("phone")
                or tags.get("contact:phone")
                or ""
            ),

            "email": (
                tags.get("email")
                or tags.get("contact:email")
                or ""
            ),

            "website": (
                tags.get("website")
                or tags.get("contact:website")
                or ""
            ),

            "source": "osm",

            "source_id": source_id,
        })

        if len(results) >= limit:
            break

    print(
        f"OSM usable businesses: {len(results)}"
    )

    return results


def build_address(tags):

    parts = []

    for key in [
        "addr:housenumber",
        "addr:street",
        "addr:suburb",
        "addr:city",
        "addr:postcode",
    ]:

        value = tags.get(key)

        if value:
            parts.append(value)

    return ", ".join(parts)