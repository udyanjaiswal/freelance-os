from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from leads.models import Lead
from projects.models import Client as ClientModel, Project


class ProjectsSecurityTests(TestCase):
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

        self.client_a_user = Client()
        self.client_a_user.login(username="user_a", password="Password123!")

        self.anon_client = Client()

        # User A entities
        self.lead_a = Lead.objects.create(
            user=self.user_a,
            business_name="Lead A",
            status="new",
        )
        self.client_model_a = ClientModel.objects.create(
            user=self.user_a,
            business_name="Client A Corp",
            name="John Doe",
        )
        self.project_a = Project.objects.create(
            client=self.client_model_a,
            project_name="Website Redesign",
            service="Web Development",
            price=1000,
            amount_paid=200,
        )

        # User B entities
        self.lead_b = Lead.objects.create(
            user=self.user_b,
            business_name="Lead B",
            status="new",
        )
        self.client_model_b = ClientModel.objects.create(
            user=self.user_b,
            business_name="Client B Corp",
            name="Jane Doe",
        )
        self.project_b = Project.objects.create(
            client=self.client_model_b,
            project_name="SEO Campaign",
            service="SEO",
            price=2000,
            amount_paid=500,
        )

    def test_unauthenticated_requests_redirect(self):
        """Unauthenticated requests to projects views must redirect to login."""
        url = reverse("client_detail", args=[self.client_model_a.id])
        response = self.anon_client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_idor_cross_user_client_detail_blocked(self):
        """User A attempting to view User B's client detail must receive 404."""
        url = reverse("client_detail", args=[self.client_model_b.id])
        response = self.client_a_user.get(url)
        self.assertEqual(response.status_code, 404)

    def test_idor_cross_user_project_detail_blocked(self):
        """User A attempting to view User B's project detail must receive 404."""
        url = reverse("project_detail", args=[self.project_b.id])
        response = self.client_a_user.get(url)
        self.assertEqual(response.status_code, 404)

    def test_idor_cross_user_project_update_blocked(self):
        """User A attempting to update User B's project must receive 404."""
        url = reverse("project_update", args=[self.project_b.id])
        response = self.client_a_user.post(url, {
            "project_name": "Hijacked Project",
            "service": "Hacked",
            "price": "9999",
            "amount_paid": "0",
        })
        self.assertEqual(response.status_code, 404)

        self.project_b.refresh_from_db()
        self.assertEqual(self.project_b.project_name, "SEO Campaign")

    def test_idor_cross_user_project_create_blocked(self):
        """User A cannot create a project under User B's client."""
        url = reverse("project_create", args=[self.client_model_b.id])
        response = self.client_a_user.post(url, {
            "project_name": "Unauthorized Project",
            "service": "Web",
        })
        self.assertEqual(response.status_code, 404)

    def test_idor_cross_user_lead_conversion_blocked(self):
        """User A cannot convert User B's lead into a client."""
        url = reverse("convert_lead_to_client", args=[self.lead_b.id])
        response = self.client_a_user.post(url)
        self.assertEqual(response.status_code, 404)

    def test_state_modifying_endpoints_reject_get(self):
        """State-modifying endpoints must reject GET requests with 405 Method Not Allowed."""
        update_url = reverse("project_update", args=[self.project_a.id])
        self.assertEqual(self.client_a_user.get(update_url).status_code, 405)

        convert_url = reverse("convert_lead_to_client", args=[self.lead_a.id])
        self.assertEqual(self.client_a_user.get(convert_url).status_code, 405)

    def test_financial_input_validation(self):
        """Verify amount_paid cannot exceed total price or be negative."""
        url = reverse("project_create", args=[self.client_model_a.id])
        response = self.client_a_user.post(url, {
            "project_name": "Test Financials",
            "service": "App Dev",
            "price": "500",
            "amount_paid": "1000",  # Invalid: paid > price
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amount paid cannot exceed total agreed price")
