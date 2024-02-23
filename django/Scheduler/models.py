from django.db import models

# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SomeTaskReview(Base):
    status = models.CharField(max_length=50, default="", null=True)
    operation = models.CharField(max_length=50, default="", null=True)
    params = models.JSONField(default=dict, null=True)
    results = models.JSONField(default=dict, null=True)

class VenvTracker(Base):
    task_id = models.CharField(max_length=50, default="", null=True)
    status = models.CharField(max_length=50, default="", null=True)
    process_id = models.IntegerField(null=True)
    cpu_utilization = models.FloatField(null=True)
    memory_utilization = models.FloatField(null=True)

class Queues(Base):
    queue_name = models.CharField(max_length=50, default="", null=True)