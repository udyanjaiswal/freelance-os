from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache


class AccountsSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.username = "alice"
        self.password = "StrongPassword!123"
        self.user = User.objects.create_user(
            username=self.username,
            email="alice@example.com",
            password=self.password,
        )

    def tearDown(self):
        cache.clear()

    def test_login_brute_force_lockout(self):
        """Verify that 5 failed login attempts trigger HTTP 429 rate limit."""
        login_url = reverse("login")

        # 5 failed login attempts
        for i in range(5):
            response = self.client.post(login_url, {
                "username": self.username,
                "password": "wrongpassword",
            })
            self.assertEqual(response.status_code, 200)

        # 6th attempt should be blocked with 429
        blocked_response = self.client.post(login_url, {
            "username": self.username,
            "password": "wrongpassword",
        })
        self.assertEqual(blocked_response.status_code, 429)
        self.assertContains(
            blocked_response,
            "Too many failed login attempts",
            status_code=429,
        )

    def test_successful_login_resets_failure_counter(self):
        """Verify that successful login clears the failed attempt counter."""
        login_url = reverse("login")

        # 3 failed attempts
        for i in range(3):
            self.client.post(login_url, {
                "username": self.username,
                "password": "wrongpassword",
            })

        # Successful login
        success_response = self.client.post(login_url, {
            "username": self.username,
            "password": self.password,
        })
        self.assertRedirects(success_response, reverse("home"))

        # Log out
        self.client.logout()

        # Counter should be reset, so a bad attempt succeeds with 200 (not blocked)
        retry_response = self.client.post(login_url, {
            "username": self.username,
            "password": "wrongpassword",
        })
        self.assertEqual(retry_response.status_code, 200)

    def test_open_redirect_defense(self):
        """Verify that external open-redirect URLs are blocked on login."""
        login_url = reverse("login")

        # External redirect attempt
        response = self.client.post(f"{login_url}?next=https://attacker-controlled.com", {
            "username": self.username,
            "password": self.password,
        })
        # Should redirect to home, NOT to external domain
        self.assertRedirects(response, reverse("home"))

        # Internal safe redirect should be honored
        self.client.logout()
        safe_response = self.client.post(f"{login_url}?next=/discover/", {
            "username": self.username,
            "password": self.password,
        })
        self.assertRedirects(safe_response, "/discover/")

    def test_logout_requires_post(self):
        """Verify that GET logout is blocked to prevent CSRF logout attacks."""
        self.client.login(username=self.username, password=self.password)
        logout_url = reverse("logout")

        # GET request must fail with 405 Method Not Allowed
        get_response = self.client.get(logout_url)
        self.assertEqual(get_response.status_code, 405)

        # POST request succeeds
        post_response = self.client.post(logout_url)
        self.assertRedirects(post_response, reverse("login"))

    def test_password_reset_rate_limiting(self):
        """Verify that password reset requests are throttled after 5 attempts."""
        reset_url = reverse("password_reset")

        for _ in range(5):
            self.client.post(reset_url, {"email": "alice@example.com"})

        # 6th attempt should be throttled
        response = self.client.post(reset_url, {"email": "alice@example.com"})
        self.assertEqual(response.status_code, 429)
