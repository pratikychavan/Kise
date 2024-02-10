from django.db import models

# Create your models here.
class SomeTaskReview(models.Model):
    status = models.CharField(max_length=50, default="", null=True)
    params = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)