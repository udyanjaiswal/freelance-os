from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from outreach.models import Campaign, CampaignLead
from leads.models import Lead


class OutreachSecurityTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            username="user_a",
            email="user_a@example.com",
            password="Password123!",
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            email="user_b@example.com",
            password="Password123!",
        )

        self.client_a = Client()
        self.client_a.login(username="user_a", password="Password123!")

        self.anon_client = Client()

        self.lead_a = Lead.objects.create(
            user=self.user_a,
            business_name="Lead Alpha",
        )
        self.campaign_a = Campaign.objects.create(
            name="Alpha Campaign",
            offer="Website redesign",
            channel="whatsapp",
            created_by=self.user_a,
        )
        self.campaign_lead_a = CampaignLead.objects.create(
            campaign=self.campaign_a,
            lead=self.lead_a,
            channel="whatsapp",
        )

        self.lead_b = Lead.objects.create(
            user=self.user_b,
            business_name="Lead Beta",
        )
        self.campaign_b = Campaign.objects.create(
            name="Beta Campaign",
            offer="SEO Services",
            channel="email",
            created_by=self.user_b,
        )
        self.campaign_lead_b = CampaignLead.objects.create(
            campaign=self.campaign_b,
            lead=self.lead_b,
            channel="email",
        )

    def test_unauthenticated_requests_redirect(self):
        """Unauthenticated requests to outreach must redirect to login."""
        url = reverse("campaign_detail", args=[self.campaign_a.id])
        response = self.anon_client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_idor_cross_user_campaign_detail_blocked(self):
        """User A attempting to view User B's campaign must receive 404."""
        url = reverse("campaign_detail", args=[self.campaign_b.id])
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 404)

    def test_idor_cross_user_generate_messages_blocked(self):
        """User A attempting to generate messages for User B's campaign must receive 404."""
        url = reverse("generate_campaign_messages", args=[self.campaign_b.id])
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 404)

    def test_generate_campaign_messages_rejects_get(self):
        """State-modifying generate_campaign_messages must reject GET with 405 Method Not Allowed."""
        url = reverse("generate_campaign_messages", args=[self.campaign_a.id])
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 405)

    def test_csrf_protection_on_generate_campaign_messages(self):
        """CSRF token must be enforced on POST to generate_campaign_messages."""
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="user_a", password="Password123!")

        url = reverse("generate_campaign_messages", args=[self.campaign_a.id])
        # POST without CSRF token should be rejected with 403 Forbidden
        response = csrf_client.post(url)
        self.assertEqual(response.status_code, 403)
