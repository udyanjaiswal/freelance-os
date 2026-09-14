from django.db import models
from django.contrib.auth.models import User

from leads.models import Lead


class Campaign(models.Model):

    CHANNEL_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("both", "WhatsApp + Email"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("ready", "Ready"),
        ("running", "Running"),
        ("completed", "Completed"),
    ]

    name = models.CharField(
        max_length=200
    )

    offer = models.CharField(
        max_length=200
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class CampaignLead(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("ready", "Ready"),
        ("approved", "Approved"),
        ("sent", "Sent"),
        ("replied", "Replied"),
        ("interested", "Interested"),
        ("follow_up", "Follow-up"),
        ("not_interested", "Not Interested"),
        ("converted", "Converted"),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="campaign_leads",
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="campaign_entries",
    )

    channel = models.CharField(
        max_length=20
    )

    message = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_campaign_leads",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "lead"],
                name="unique_campaign_lead",
            )
        ]

    def __str__(self):
        return (
            f"{self.campaign.name} - "
            f"{self.lead.business_name}"
        )


class Outreach(models.Model):

    METHOD_CHOICES = [
        ("call", "Call"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
    ]

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="outreach_records",
    )

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
    )

    message = models.TextField(
        blank=True
    )

    outcome = models.CharField(
        max_length=255,
        blank=True
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.lead.business_name} - "
            f"{self.method}"
        )