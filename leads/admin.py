from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'business_name',
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
    