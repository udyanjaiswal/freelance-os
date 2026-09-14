import re


GENERIC_WORDS = {
    "salon",
    "saloon",
    "spa",
    "beauty",
    "parlor",
    "parlour",
    "studio",
    "unisex",
}


def normalize_text(value):
    if not value:
        return ""

    value = value.lower()

    # Remove punctuation
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    # Remove generic business words
    words = [
        word
        for word in value.split()
        if word not in GENERIC_WORDS
    ]

    return " ".join(words)


def normalize_phone(value):
    if not value:
        return ""

    return "".join(
        character
        for character in value
        if character.isdigit()
    )


def normalize_lead(data):
    data = data.copy()

    data["business_name"] = data.get(
        "business_name", ""
    ).strip()

    data["city"] = data.get(
        "city", ""
    ).strip()

    data["phone"] = data.get(
        "phone", ""
    ).strip()

    data["email"] = data.get(
        "email", ""
    ).strip()

    data["website"] = data.get(
        "website", ""
    ).strip()

    data["_normalized_name"] = normalize_text(
        data["business_name"]
    )

    data["_normalized_city"] = normalize_text(
        data["city"]
    )

    data["_normalized_phone"] = normalize_phone(
        data["phone"]
    )

    return data