from django.shortcuts import render
from django.utils import timezone

from leads.models import Lead
from outreach.models import CampaignLead, Outreach
from django.contrib.auth.decorators import login_required

def landing(request):
    return render(request, "landing.html")


@login_required
def home(request):
    # Only current user's leads
    leads = (
        Lead.objects
        .filter(user=request.user)
        .order_by("-score")
    )

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
    # Outreach belongs to a Lead,
    # so filter through lead's user.
    manual_follow_ups = (
        Outreach.objects
        .filter(
            lead__user=request.user,
            follow_up_date__isnull=False,
        )
        .select_related("lead")
        .order_by("follow_up_date")[:10]
    )

    # Campaign follow-ups
    # Campaign already has created_by → User.
    campaign_follow_ups = (
        CampaignLead.objects
        .filter(
            campaign__created_by=request.user,
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

        "total_leads": Lead.objects.filter(
            user=request.user
        ).count(),

        "high_leads": Lead.objects.filter(
            user=request.user,
            potential="high",
        ).count(),

        "medium_leads": Lead.objects.filter(
            user=request.user,
            potential="medium",
        ).count(),

        "low_leads": Lead.objects.filter(
            user=request.user,
            potential="low",
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