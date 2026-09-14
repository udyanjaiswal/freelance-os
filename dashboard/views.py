from django.shortcuts import render
from leads.models import Lead


def home(request):
    leads = Lead.objects.all().order_by('-score')

    search = request.GET.get('search', '')
    potential = request.GET.get('potential', '')

    if search:
        leads = leads.filter(
            business_name__icontains=search
        ) | leads.filter(
            city__icontains=search
        ) | leads.filter(
            phone__icontains=search
        )

    if potential:
        leads = leads.filter(potential=potential)

    context = {
        'leads': leads,
        'total_leads': Lead.objects.count(),
        'high_leads': Lead.objects.filter(potential='high').count(),
        'medium_leads': Lead.objects.filter(potential='medium').count(),
        'low_leads': Lead.objects.filter(potential='low').count(),
    }

    return render(request, 'dashboard/home.html', context)