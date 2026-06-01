import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_analysis.settings")
django.setup()

from apps.analysis.views import location_distribution
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/api/analysis/location/')
response = location_distribution(request)
print(response.data)