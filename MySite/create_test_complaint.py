import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MySite.settings')
django.setup()

from API.models import Complaint

# Create test complaint
complaint = Complaint.objects.create(
    user_id='testuser',
    location='Test Location',
    description='This is a test complaint',
    severity='high',
    status='pending'
)
print(f"Created test complaint ID: {complaint.id}")
print(f"Total complaints now: {Complaint.objects.count()}")
