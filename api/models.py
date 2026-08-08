from django.db import models

# Create your models here.

class Note(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True, default=list)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (self.title or self.body or "")[0:69]