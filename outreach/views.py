from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from leads.models import Lead

from .models import Campaign, CampaignLead

from .message_generator import generate_message
from django.contrib.auth.decorators import login_required

@login_required
def campaign_list(request):
    campaigns = (
        Campaign.objects
        .filter(created_by=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "outreach/campaign_list.html",
        {
            "campaigns": campaigns,
        },
    )

@login_required
def campaign_create(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        offer = request.POST.get("offer", "").strip()
        channel = request.POST.get("channel")

        potential = request.POST.get("potential")
        city = request.POST.get("city", "").strip()
        category = request.POST.get("category", "").strip()
        website = request.POST.get("website")
        status = request.POST.get("status")

        campaign = Campaign.objects.create(
            name=name,
            offer=offer,
            channel=channel,
            status="draft",
            created_by=request.user,
        )

        # -------------------------
        # FIND TARGET LEADS
        # -------------------------

        # Only current user's leads
        leads = Lead.objects.filter(
            user=request.user
        )

        if potential and potential != "all":
            leads = leads.filter(
                potential=potential
            )

        if city:
            leads = leads.filter(
                city__icontains=city
            )

        if category:
            leads = leads.filter(
                category__icontains=category
            )

        if status and status != "all":
            leads = leads.filter(
                status=status
            )

        # Website targeting
        if website == "no_website":

            leads = leads.filter(
                website=""
            )

        elif website == "map_only":

            leads = [
                lead
                for lead in leads
                if lead.website
                and (
                    "google.com" in lead.website
                    or "goo.gl" in lead.website
                    or "maps.app.goo.gl" in lead.website
                )
            ]

        elif website == "has_website":

            leads = [
                lead
                for lead in leads
                if lead.website
                and not (
                    "google.com" in lead.website
                    or "goo.gl" in lead.website
                    or "maps.app.goo.gl" in lead.website
                )
            ]

        # -------------------------
        # CREATE CAMPAIGN LEADS
        # -------------------------

        for lead in leads:

            CampaignLead.objects.get_or_create(
                campaign=campaign,
                lead=lead,
                defaults={
                    "channel": channel,
                },
            )

        return redirect(
            "campaign_detail",
            campaign_id=campaign.id,
        )

    return render(
        request,
        "outreach/campaign_create.html",
        {
            "status_choices": Lead.STATUS_CHOICES,
        },
    )

@login_required
def campaign_detail(request, campaign_id):

    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        created_by=request.user,
    )

    campaign_leads = (
        campaign.campaign_leads
        .select_related("lead")
        .order_by("-lead__score")
    )

    return render(
        request,
        "outreach/campaign_detail.html",
        {
            "campaign": campaign,
            "campaign_leads": campaign_leads,
        },
    )

@login_required
def generate_campaign_messages(request, campaign_id):

    campaign = get_object_or_404(
        Campaign,
        id=campaign_id,
        created_by=request.user,
    )

    campaign_leads = campaign.campaign_leads.all()

    success_count = 0
    failed_count = 0

    for campaign_lead in campaign_leads:

        # Don't regenerate messages that already exist
        if campaign_lead.message:
            continue

        try:
            campaign_lead.message = generate_message(
                campaign_lead
            )

            campaign_lead.status = "ready"

            campaign_lead.save(
                update_fields=[
                    "message",
                    "status",
                    "updated_at",
                ]
            )

            success_count += 1

        except Exception as error:
            print(
                f"Message generation failed for "
                f"{campaign_lead.lead.business_name}: {error}"
            )

            campaign_lead.status = "failed"

            campaign_lead.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            failed_count += 1

    # Campaign is ready if at least one message was generated.
    if success_count > 0:
        campaign.status = "ready"

    campaign.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    if failed_count > 0:
        messages.warning(
            request,
            f"{success_count} message(s) generated successfully. "
            f"{failed_count} message(s) failed because the AI "
            f"service was temporarily unavailable. "
            f"You can retry them later."
        )

    elif success_count > 0:
        messages.success(
            request,
            f"{success_count} message(s) generated successfully."
        )

    else:
        messages.info(
            request,
            "No new messages needed to be generated."
        )

    return redirect(
        "campaign_detail",
        campaign_id=campaign.id,
    )