from django.shortcuts import get_object_or_404, redirect, render

from leads.models import Lead
from .models import Client, Project


def convert_lead_to_client(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method != "POST":
        return redirect("lead_detail", lead_id=lead.id)

    if hasattr(lead, "client"):
        return redirect("client_detail", client_id=lead.client.id)

    client = Client.objects.create(
        lead=lead,
        name=lead.business_name,
        business_name=lead.business_name,
        phone=lead.phone,
        email=lead.email,
        notes=lead.notes,
    )

    lead.status = "converted"
    lead.save(update_fields=["status", "updated_at"])

    return redirect("client_detail", client_id=client.id)


def client_list(request):
    clients = Client.objects.all().order_by("-created_at")

    return render(
        request,
        "projects/client_list.html",
        {"clients": clients},
    )


def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    projects = client.projects.all().order_by("-created_at")

    return render(
        request,
        "projects/client_detail.html",
        {
            "client": client,
            "projects": projects,
        },
    )


def project_create(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        Project.objects.create(
            client=client,
            project_name=request.POST.get("project_name", "").strip(),
            service=request.POST.get("service", "").strip(),
            status=request.POST.get("status", "planning"),
            start_date=request.POST.get("start_date") or None,
            deadline=request.POST.get("deadline") or None,
            price=request.POST.get("price") or 0,
            amount_paid=request.POST.get("amount_paid") or 0,
            domain_name=request.POST.get("domain_name", "").strip(),
            domain_provider=request.POST.get("domain_provider", "").strip(),
            domain_renewal_date=request.POST.get("domain_renewal_date") or None,
            hosting_provider=request.POST.get("hosting_provider", "").strip(),
            hosting_plan=request.POST.get("hosting_plan", "").strip(),
            hosting_renewal_date=request.POST.get("hosting_renewal_date") or None,
            notes=request.POST.get("notes", "").strip(),
        )

        return redirect("client_detail", client_id=client.id)

    return render(
        request,
        "projects/project_create.html",
        {
            "client": client,
            "status_choices": Project.STATUS_CHOICES,
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("client"),
        id=project_id,
    )

    return render(
        request,
        "projects/project_detail.html",
        {"project": project},
    )


def project_update(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.project_name = request.POST.get(
            "project_name", project.project_name
        )
        project.service = request.POST.get(
            "service", project.service
        )
        project.status = request.POST.get(
            "status", project.status
        )

        project.start_date = request.POST.get("start_date") or None
        project.deadline = request.POST.get("deadline") or None

        project.price = request.POST.get("price") or 0
        project.amount_paid = request.POST.get("amount_paid") or 0

        project.domain_name = request.POST.get(
            "domain_name", ""
        ).strip()

        project.domain_provider = request.POST.get(
            "domain_provider", ""
        ).strip()

        project.domain_renewal_date = (
            request.POST.get("domain_renewal_date") or None
        )

        project.hosting_provider = request.POST.get(
            "hosting_provider", ""
        ).strip()

        project.hosting_plan = request.POST.get(
            "hosting_plan", ""
        ).strip()

        project.hosting_renewal_date = (
            request.POST.get("hosting_renewal_date") or None
        )

        project.notes = request.POST.get(
            "notes", ""
        ).strip()

        project.save()

    return redirect("project_detail", project_id=project.id)