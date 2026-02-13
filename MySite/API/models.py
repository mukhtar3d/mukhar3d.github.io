from django.db import models
from django.contrib.auth.hashers import make_password, check_password

ROLE_CHOICES = [
    ('admin', 'admin'),
    ('moderator', 'moderator'),
    ('user', 'user'),
]

class AppUser(models.Model):
    user_id = models.CharField(max_length=12, primary_key=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def set_password(self, raw):
        self.password = make_password(raw)
        # Don't save here - let the caller decide when to save

    def check_password(self, raw):
        return check_password(raw, self.password)

    def __str__(self):
        return f"{self.user_id} ({self.role})"

    class Meta:
        app_label = 'API'

SEVERITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_review', 'In Review'),
    ('resolved', 'Resolved'),
]

class Complaint(models.Model):
    user_id = models.CharField(max_length=12, null=True, blank=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint {self.id} - {self.severity}"

    class Meta:
        app_label = 'API'
