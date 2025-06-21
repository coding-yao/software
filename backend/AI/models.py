from django.db import models

class APIKey(models.Model):
    SERVICE_CHOICES = [
        ('DEEPSEEK', 'DeepSeek'),
        ('GLM', 'GLM-4V'),
    ]
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    key = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_service_display()} Key"
