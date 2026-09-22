from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .engine import discover_leads


def parse_search_query(search):

    search = search.strip()

    if not search:
        return None, None

    search_lower = search.lower()

    # Main V1 pattern:
    # "salons in Lucknow"
    if " in " in search_lower:

        position = search_lower.rfind(" in ")

        query = search[:position].strip()
        city = search[position + 4:].strip()

        if query and city:
            return query, city

    return search, ""


@login_required
def discover(request):

    result = None
    search = ""

    if request.method == "POST":

        search = request.POST.get("search", "").strip()

        limit = int(
            request.POST.get("limit", 100)
        )

        query, city = parse_search_query(search)

        if query and city:

            result = discover_leads(
                query=query,
                city=city,
                limit=limit,
                user=request.user,
            )

    return render(
        request,
        "discovery/discover.html",
        {
            "result": result,
            "search": search,
        }
    )