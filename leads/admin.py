from django.contrib import admin
from .models import Lead


class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'business_name',
        'user',
        'category',
        'city',
        'score',
        'potential',
        'status',
    )

    list_filter = (
        'potential',
        'status',
        'category',
        'source',
    )

    search_fields = (
        'business_name',
        'phone',
        'email',
        'city',
    )

    def get_queryset(self, request):
        """Restrict admin list to the logged-in user's own leads.
        Superusers see all leads (intended for debugging only — remove in prod)."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
