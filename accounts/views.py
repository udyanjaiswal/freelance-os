from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import SignupForm

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_TIME = 300  # 5 minutes in seconds


def get_client_ip(request):
    """Safely extracts client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    ip = get_client_ip(request)

    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        attempt_key = f"login_attempts_{ip}_{username}"
        ip_attempt_key = f"login_attempts_ip_{ip}"

        attempts = cache.get(attempt_key, 0)
        ip_attempts = cache.get(ip_attempt_key, 0)

        # Brute-force lockout check
        if attempts >= MAX_LOGIN_ATTEMPTS or ip_attempts >= MAX_LOGIN_ATTEMPTS * 3:
            return render(
                request,
                "accounts/login.html",
                {
                    "form": AuthenticationForm(request),
                    "rate_limit_error": (
                        "Too many failed login attempts. "
                        "Please wait 5 minutes before trying again."
                    ),
                },
                status=429,
            )

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Clear failure counters on successful login
            cache.delete(attempt_key)
            cache.delete(ip_attempt_key)

            # Open-redirect guard: only use `next` if it is a safe relative URL
            next_url = request.POST.get("next") or request.GET.get("next", "")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("home")

        else:
            # Increment failed attempts on bad credentials
            cache.set(attempt_key, attempts + 1, LOGIN_LOCKOUT_TIME)
            cache.set(ip_attempt_key, ip_attempts + 1, LOGIN_LOCKOUT_TIME)

    else:
        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


class RateLimitedPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            ip = get_client_ip(request)
            key = f"pw_reset_ip_{ip}"
            attempts = cache.get(key, 0)
            if attempts >= 5:
                messages.error(
                    request,
                    "Too many password reset requests. Please wait a few minutes before trying again."
                )
                return render(request, self.template_name, {"form": self.get_form()}, status=429)
            cache.set(key, attempts + 1, 600)  # 10 minute window
        return super().dispatch(request, *args, **kwargs)


@require_POST  # GET logout is a CSRF attack vector — block it
def logout_view(request):
    logout(request)
    response = redirect("login")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response