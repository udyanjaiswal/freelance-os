from .normalize import normalize_lead


def find_match(leads, incoming):
    incoming = normalize_lead(incoming)

    incoming_phone = incoming["_normalized_phone"]
    incoming_name = incoming["_normalized_name"]
    incoming_city = incoming["_normalized_city"]

    for lead in leads:

        existing = normalize_lead(lead)

        existing_phone = existing["_normalized_phone"]
        existing_name = existing["_normalized_name"]
        existing_city = existing["_normalized_city"]

        
        # 1. Phone match
        

        if (
            incoming_phone
            and existing_phone
            and incoming_phone == existing_phone
        ):
            return lead

        
        # 2. Exact name + city
        

        if (
            incoming_name
            and existing_name
            and incoming_city
            and existing_city
            and incoming_name == existing_name
            and incoming_city == existing_city
        ):
            return lead

        
        # 3. Name contains match
        

        if (
            incoming_name
            and existing_name
            and incoming_city
            and existing_city
            and incoming_city == existing_city
        ):
            if (
                incoming_name in existing_name
                or existing_name in incoming_name
            ):
                return lead

    return None


def merge_leads(existing, incoming):
    fields = [
        "business_name",
        "category",
        "address",
        "city",
        "phone",
        "email",
        "website",
    ]

    for field in fields:

        if (
            not existing.get(field)
            and incoming.get(field)
        ):
            existing[field] = incoming[field]

    return existing 