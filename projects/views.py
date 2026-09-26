from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from leads.models import Lead
from .models import Client, Project
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation


@login_required
@require_POST
def convert_lead_to_client(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        user=request.user,
    )

    if hasattr(lead, "client"):
        return redirect("client_detail", client_id=lead.client.id)

    client = Client.objects.create(
        user=request.user,
        lead=lead,
        name=lead.business_name,
        business_name=lead.business_name,
        phone=lead.phone,
        email=lead.email,
        notes=lead.notes,
    )

    lead.status = "converted"
    lead.save(update_fields=["status", "updated_at"])

    return redirect(
        "client_detail",
        client_id=client.id,
    )


@login_required
def client_list(request):
    clients = (
        Client.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "projects/client_list.html",
        {"clients": clients},
    )


@login_required
def client_create(request):
    if request.method == "POST":
        business_name = request.POST.get(
            "business_name",
            "",
        ).strip()

        name = request.POST.get(
            "name",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        notes = request.POST.get(
            "notes",
            "",
        ).strip()

        if not business_name:
            return render(
                request,
                "projects/client_create.html",
                {
                    "error": "Business name is required.",
                    "form_data": request.POST,
                },
            )

        if email:
            try:
                validate_email(email)
            except ValidationError:
                return render(
                    request,
                    "projects/client_create.html",
                    {
                        "error": "Please enter a valid email address.",
                        "form_data": request.POST,
                    },
                )

        client = Client.objects.create(
            user=request.user,
            lead=None,
            name=name,
            business_name=business_name,
            phone=phone,
            email=email,
            notes=notes,
        )

        return redirect(
            "client_detail",
            client_id=client.id,
        )

    return render(
        request,
        "projects/client_create.html",
    )


@login_required
def client_detail(request, client_id):
    client = get_object_or_404(
        Client,
        id=client_id,
        user=request.user,
    )

    projects = client.projects.all().order_by("-created_at")

    return render(
        request,
        "projects/client_detail.html",
        {
            "client": client,
            "projects": projects,
        },
    )


@login_required
def project_create(request, client_id):
    client = get_object_or_404(
        Client,
        id=client_id,
        user=request.user,
    )

    if request.method == "POST":
        project_name = request.POST.get("project_name", "").strip()
        service = request.POST.get("service", "").strip()
        status = request.POST.get("status", "planning").strip()

        errors = []
        # V2: Validate required fields
        if not project_name:
            errors.append("Project name is required.")
        if not service:
            errors.append("Service is required.")

        # V3: Validate status
        valid_statuses = [choice[0] for choice in Project.STATUS_CHOICES]
        if status not in valid_statuses:
            errors.append(f"'{status}' is not a valid project status.")

        # B2/B3: parse and sanitize price and amount_paid to integers
        raw_price = request.POST.get("price", "").strip()
        try:
            price = int(Decimal(raw_price)) if raw_price else 0
            if price < 0:
                errors.append("Price cannot be negative.")
        except (InvalidOperation, ValueError, TypeError):
            errors.append("Price must be a valid number.")
            price = 0

        raw_paid = request.POST.get("amount_paid", "").strip()
        try:
            amount_paid = int(Decimal(raw_paid)) if raw_paid else 0
            if amount_paid < 0:
                errors.append("Amount paid cannot be negative.")
        except (InvalidOperation, ValueError, TypeError):
            errors.append("Amount paid must be a valid number.")
            amount_paid = 0

        # D1: Prevent amount_paid > price
        if not errors and amount_paid > price:
            errors.append("Amount paid cannot exceed total agreed price.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "projects/project_create.html",
                {
                    "client": client,
                    "status_choices": Project.STATUS_CHOICES,
                    "form_data": request.POST,
                },
            )

        project = Project.objects.create(
            client=client,
            project_name=project_name,
            service=service,
            status=status,
            start_date=request.POST.get("start_date") or None,
            deadline=request.POST.get("deadline") or None,
            price=price,
            amount_paid=amount_paid,
            domain_name=request.POST.get("domain_name", "").strip(),
            domain_provider=request.POST.get("domain_provider", "").strip(),
            domain_renewal_date=request.POST.get("domain_renewal_date") or None,
            hosting_provider=request.POST.get("hosting_provider", "").strip(),
            hosting_plan=request.POST.get("hosting_plan", "").strip(),
            hosting_renewal_date=request.POST.get("hosting_renewal_date") or None,
            notes=request.POST.get("notes", "").strip(),
        )

        messages.success(request, f"Project '{project.project_name}' created successfully.")
        return redirect(
            "client_detail",
            client_id=client.id,
        )

    return render(
        request,
        "projects/project_create.html",
        {
            "client": client,
            "status_choices": Project.STATUS_CHOICES,
        },
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("client"),
        id=project_id,
        client__user=request.user,
    )

    return render(
        request,
        "projects/project_detail.html",
        {"project": project},
    )


@login_required
@require_POST
def project_update(request, project_id):
    # B1: verify ownership and existence
    project = get_object_or_404(
        Project,
        id=project_id,
        client__user=request.user,
    )

    project_name = request.POST.get("project_name", "").strip() or project.project_name
    service = request.POST.get("service", "").strip() or project.service
    status = request.POST.get("status", project.status).strip()

    # V3: validate status
    valid_statuses = [choice[0] for choice in Project.STATUS_CHOICES]
    if status not in valid_statuses:
        messages.error(request, f"'{status}' is not a valid project status.")
        return redirect("project_detail", project_id=project.id)

    # B2/B3: parse and sanitize price and amount_paid
    raw_price = request.POST.get("price", "").strip()
    try:
        price = int(Decimal(raw_price)) if raw_price else 0
        if price < 0:
            messages.error(request, "Price cannot be negative.")
            return redirect("project_detail", project_id=project.id)
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, "Price must be a valid number.")
        return redirect("project_detail", project_id=project.id)

    raw_paid = request.POST.get("amount_paid", "").strip()
    try:
        amount_paid = int(Decimal(raw_paid)) if raw_paid else 0
        if amount_paid < 0:
            messages.error(request, "Amount paid cannot be negative.")
            return redirect("project_detail", project_id=project.id)
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, "Amount paid must be a valid number.")
        return redirect("project_detail", project_id=project.id)

    # D1: Prevent amount_paid > price
    if amount_paid > price:
        messages.error(request, "Amount paid cannot exceed total agreed price.")
        return redirect("project_detail", project_id=project.id)

    project.project_name = project_name
    project.service = service
    project.status = status
    project.start_date = request.POST.get("start_date") or None
    project.deadline = request.POST.get("deadline") or None
    project.price = price
    project.amount_paid = amount_paid
    project.domain_name = request.POST.get("domain_name", "").strip()
    project.domain_provider = request.POST.get("domain_provider", "").strip()
    project.domain_renewal_date = (
        request.POST.get("domain_renewal_date") or None
    )
    project.hosting_provider = request.POST.get("hosting_provider", "").strip()
    project.hosting_plan = request.POST.get("hosting_plan", "").strip()
    project.hosting_renewal_date = (
        request.POST.get("hosting_renewal_date") or None
    )
    project.notes = request.POST.get("notes", "").strip()

    project.save()
    messages.success(request, "Project details updated successfully.")

    return redirect(
        "project_detail",
        project_id=project.id,
    )