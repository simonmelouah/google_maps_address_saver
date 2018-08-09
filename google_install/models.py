from django.db import models

class GoogleUser(models.Model):
    """Google user model."""

    access_token = models.CharField(max_length=128, null=True)
    refresh_token = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    uninstalled = models.NullBooleanField(default=False, null=True)
