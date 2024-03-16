from django.db import models
from django.contrib.auth.models import User

QUEUE_TYPES = (
    ('Task', 'Task'),
    ('Control', 'Control'),
    ('Result', 'Result')
)

# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Queues(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user-queue")
    queue_name = models.CharField(max_length=255, default="", null=True)
    queue_type = models.CharField(max_length=50, default="", null=True, choices=QUEUE_TYPES)


class Worker(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user-worker")
    queue_name = models.ForeignKey(Queues, on_delete=models.CASCADE, related_name="worker-queue")
    worker_name = models.CharField(max_length=50, default="", null=True)


class Task(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user-task")
    status = models.CharField(max_length=50, default="", null=True)
    operation = models.CharField(max_length=50, default="", null=True)
    params = models.JSONField(default=dict, null=True)
    results = models.JSONField(default=dict, null=True)


class VirtualEnvironments(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user-venv")
    worker_name = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="worker-venv")
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task-venv")
    status = models.CharField(max_length=50, default="", null=True)
    process_id = models.IntegerField(null=True)
    cpu_utilization = models.FloatField(null=True)
    memory_utilization = models.FloatField(null=True)