import requests


def enrich_lead(lead):
    """
    Basic V1 enrichment.
    Checks whether an existing website is reachable.
    """

    result = {
        "website_status": None,
    }

    if not lead.website:
        return result

    website = lead.website.strip()

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    try:
        response = requests.get(
            website,
            timeout=8,
            allow_redirects=True,
            headers={
                "User-Agent": "FreelancerOS/1.0"
            },
        )

        if response.ok:
            result["website_status"] = "working"
        else:
            result["website_status"] = "not_working"

    except requests.RequestException:
        result["website_status"] = "not_working"

    return result