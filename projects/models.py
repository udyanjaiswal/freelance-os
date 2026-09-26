from django.db import models
from leads.models import Lead
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="clients",
)

    lead = models.OneToOneField(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client",
    )

    name = models.CharField(max_length=150)
    business_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class Project(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("review", "Review"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    project_name = models.CharField(max_length=200)
    service = models.CharField(max_length=200)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="planning",
    )

    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    price = models.PositiveIntegerField(default=0)

    amount_paid = models.PositiveIntegerField(default=0)

    domain_name = models.CharField(max_length=255, blank=True)
    domain_provider = models.CharField(max_length=100, blank=True)
    domain_renewal_date = models.DateField(null=True, blank=True)

    hosting_provider = models.CharField(max_length=100, blank=True)
    hosting_plan = models.CharField(max_length=150, blank=True)
    hosting_renewal_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def balance(self):
        return self.price - self.amount_paid

    def __str__(self):
        return self.project_name