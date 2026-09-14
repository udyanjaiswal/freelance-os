import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['GEMINI_API_KEY'] = 'dummy'
django.setup()

from django.test import Client
from leads.models import Lead
from outreach.models import Campaign
from projects.models import Client as ClientModel, Project

c = Client(SERVER_NAME='localhost')

routes = [
    ('/', 'Home / Leads'),
    ('/discover/', 'Discover'),
]

first_lead = Lead.objects.first()
if first_lead:
    routes.append((f'/leads/{first_lead.id}/', f'Lead Detail ({first_lead.business_name})'))

routes.append(('/outreach/', 'Campaign List'))
routes.append(('/outreach/create/', 'Campaign Create'))

first_campaign = Campaign.objects.first()
if first_campaign:
    routes.append((f'/outreach/{first_campaign.id}/', f'Campaign Detail ({first_campaign.name})'))

routes.append(('/projects/clients/', 'Client List'))

first_client = ClientModel.objects.first()
if first_client:
    routes.append((f'/projects/clients/{first_client.id}/', f'Client Detail ({first_client.business_name})'))
    routes.append((f'/projects/clients/{first_client.id}/projects/create/', f'Project Create ({first_client.business_name})'))

first_project = Project.objects.first()
if first_project:
    routes.append((f'/projects/projects/{first_project.id}/', f'Project Detail ({first_project.project_name})'))

print("--- Testing Routes ---")
all_passed = True
for url, name in routes:
    response = c.get(url)
    status = response.status_code
    if status == 200:
        print(f"[PASS] {status} {name}: {url}")
    else:
        print(f"[FAIL] {status} {name}: {url}")
        all_passed = False

if all_passed:
    print("ALL ROUTES RETURNED HTTP 200 OK!")
else:
    print("SOME ROUTES FAILED!")
