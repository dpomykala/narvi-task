from django.db import models


class GroupingTask(models.Model):
    input_data = models.JSONField()
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
