from django.shortcuts import get_object_or_404, redirect, render

from .models import Lead
from outreach.models import Outreach
from scoring.engine import get_score_breakdown
from django.contrib.auth.decorators import login_required

@login_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        user=request.user,
    )

    # Save notes
    if request.method == "POST":
        notes = request.POST.get("notes")

        if notes is not None:
            lead.notes = notes
            lead.save(
                update_fields=[
                    "notes",
                    "updated_at",
                ]
            )

    score, breakdown = get_score_breakdown(lead)

    outreach_records = lead.outreach_records.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "leads/lead_detail.html",
        {
            "lead": lead,
            "score": score,
            "breakdown": breakdown,
            "outreach_records": outreach_records,
        },
    )

@login_required
def update_status(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        user=request.user,
    )

    if request.method == "POST":

        status = request.POST.get("status")

        valid_statuses = [
            choice[0]
            for choice in Lead.STATUS_CHOICES
        ]

        if status in valid_statuses:

            lead.status = status

            lead.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    return redirect(
        "lead_detail",
        lead_id=lead.id
    )

@login_required
def add_outreach(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        user=request.user,
    )

    if request.method == "POST":

        Outreach.objects.create(
            lead=lead,
            method=request.POST.get("method"),
            message=request.POST.get("message", ""),
            outcome=request.POST.get("outcome", ""),
            follow_up_date=(
                request.POST.get("follow_up_date")
                or None
            ),
        )

        # First outreach automatically moves
        # a new lead to contacted.
        if lead.status == "new":

            lead.status = "contacted"

            lead.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

    return redirect(
        "lead_detail",
        lead_id=lead.id
    )