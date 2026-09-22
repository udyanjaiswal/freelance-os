
from leads.models import Lead

from discovery.sources.osm import search_osm
from discovery.sources.foursquare import search_foursquare
from discovery.normalize import normalize_lead
from discovery.dedupe import find_match, merge_leads

from scoring.enrichment import enrich_lead
from scoring.engine import score_lead

def discover_leads(query, city, limit=20):
    all_results = []

    try:
        osm_results = search_osm(query, city, limit)
    except Exception as error:
        print(f"OSM unavailable: {error}")
        osm_results = []

    all_results.extend(osm_results)

    try:
        foursquare_results = search_foursquare(
            query, city, limit
        )
    except Exception as error:
        print(f"Foursquare unavailable: {error}")
        foursquare_results = []

    all_results.extend(foursquare_results)

    unique_results = []

    for data in all_results:
        data = normalize_lead(data)
        match = find_match(unique_results, data)

        if match:
            merge_leads(match, data)

            sources = set(match.get("source", "").split(","))
            sources.add(data.get("source", ""))
            match["source"] = ",".join(
                source for source in sources if source
            )
        else:
            unique_results.append(data)

    new_count = 0
    duplicate_count = 0

    for data in unique_results:
        _, is_new = save_lead_data(data)

        if is_new:
            new_count += 1
        else:
            duplicate_count += 1

    return {
        "found": len(all_results),
        "new": new_count,
        "duplicates": duplicate_count,
    }

def save_lead_data(data):
    data = data.copy()

    # Remove internal normalization keys
    data.pop("_normalized_name", None)
    data.pop("_normalized_city", None)
    data.pop("_normalized_phone", None)

    incoming = normalize_lead(data)

    existing = None

    # Exact provider match first
    if data.get("source_id"):
        existing = Lead.objects.filter(
            source_id=data["source_id"]
        ).first()

    # Cross-source database match
    if not existing:
        for lead in Lead.objects.all():

            stored = normalize_lead({
                "business_name": lead.business_name,
                "city": lead.city,
                "phone": lead.phone,
            })

            # Phone match
            if (
                incoming["_normalized_phone"]
                and stored["_normalized_phone"]
                and incoming["_normalized_phone"]
                == stored["_normalized_phone"]
            ):
                existing = lead
                break

            # Name + city match
            if (
                incoming["_normalized_name"]
                and incoming["_normalized_city"]
                and incoming["_normalized_name"]
                == stored["_normalized_name"]
                and incoming["_normalized_city"]
                == stored["_normalized_city"]
            ):
                existing = lead
                break

            # Name contains match
            if (
                incoming["_normalized_name"]
                and stored["_normalized_name"]
                and incoming["_normalized_city"]
                == stored["_normalized_city"]
                and (
                    incoming["_normalized_name"]
                    in stored["_normalized_name"]
                    or stored["_normalized_name"]
                    in incoming["_normalized_name"]
                )
            ):
                existing = lead
                break

    # Existing lead: merge missing fields
    if existing:

        for field in [
            "business_name",
            "category",
            "address",
            "city",
            "phone",
            "email",
            "website",
        ]:
            if (
                not getattr(existing, field)
                and data.get(field)
            ):
                setattr(existing, field, data[field])

        # Merge source information
        existing_sources = set(
            existing.source.split(",")
        )

        new_sources = set(
            data.get("source", "").split(",")
        )

        existing.source = ",".join(
            sorted(
                source
                for source in existing_sources | new_sources
                if source
            )
        )

        existing.save()

        enrich_lead(existing)
        score_lead(existing)

        return existing, False

    # New lead: allow only valid model fields
    allowed_fields = {
        "business_name",
        "category",
        "address",
        "city",
        "phone",
        "email",
        "website",
        "source",
        "source_id",
        "notes",
    }

    lead_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    lead = Lead.objects.create(**lead_data)

    enrich_lead(lead)
    score_lead(lead)

    return lead, True


def discover_leads(query, city, limit=20):

    all_results = []

    # OSM Logic
    try:
        osm_results = search_osm(query, city, limit)
    except Exception as error:
        print(f"OSM unavailable: {error}")
        osm_results = []

    all_results.extend(osm_results)

    # Foursquare Logic
    try:
        foursquare_results = search_foursquare(
            query,
            city,
            limit
        )
    except Exception as error:
        print(f"Foursquare unavailable: {error}")
        foursquare_results = []

    all_results.extend(foursquare_results)

    print(f"Total raw results: {len(all_results)}")

    # Merge provider results
    unique_results = []

    for data in all_results:

        data = normalize_lead(data)

        match = find_match(unique_results, data)

        if match:
            merge_leads(match, data)

            # Keep track of both sources
            sources = set(
                match.get("source", "").split(",")
            )
            sources.add(data.get("source", ""))

            match["source"] = ",".join(
                source for source in sources if source
            )

        else:
            unique_results.append(data)

    print(
        f"Unique results after provider deduplication: "
        f"{len(unique_results)}"
    )

    new_count = 0
    duplicate_count = 0

    # Save results using reusable function
    for data in unique_results:

        _, is_new = save_lead_data(data)

        if is_new:
            new_count += 1
        else:
            duplicate_count += 1

    return {
        "found": len(all_results),
        "new": new_count,
        "duplicates": duplicate_count,
    }