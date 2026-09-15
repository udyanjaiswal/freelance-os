from django.shortcuts import render
from django.utils import timezone

from leads.models import Lead
from outreach.models import CampaignLead, Outreach


def home(request):
    leads = Lead.objects.all().order_by("-score")

    search = request.GET.get("search", "")
    potential = request.GET.get("potential", "")

    if search:
        leads = (
            leads.filter(business_name__icontains=search)
            | leads.filter(city__icontains=search)
            | leads.filter(phone__icontains=search)
        )

    if potential:
        leads = leads.filter(potential=potential)

    today = timezone.localdate()

    # Manual outreach follow-ups
    manual_follow_ups = (
        Outreach.objects
        .filter(follow_up_date__isnull=False)
        .select_related("lead")
        .order_by("follow_up_date")[:10]
    )

    # Campaign follow-ups
    campaign_follow_ups = (
        CampaignLead.objects
        .filter(
            follow_up_date__isnull=False,
            status__in=[
                "follow_up",
                "sent",
                "replied",
                "interested",
            ],
        )
        .select_related("lead", "campaign")
        .order_by("follow_up_date")[:10]
    )

    context = {
        "leads": leads,

        "total_leads": Lead.objects.count(),
        "high_leads": Lead.objects.filter(
            potential="high"
        ).count(),
        "medium_leads": Lead.objects.filter(
            potential="medium"
        ).count(),
        "low_leads": Lead.objects.filter(
            potential="low"
        ).count(),

        "manual_follow_ups": manual_follow_ups,
        "campaign_follow_ups": campaign_follow_ups,

        "today": today,
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )