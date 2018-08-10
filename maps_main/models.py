from django.db import models

class FusionTable(models.Model):
    """Google fusion table reference model."""

    google_user = models.ForeignKey(
        'google_install.GoogleUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True)
    google_id = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """Name of table returned."""
        return self.name


class Address(models.Model):
    """Address model for storing all addresses clicked."""

    fusion_table = models.ForeignKey(
        FusionTable, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    full_address = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """Address returned."""
        return self.full_address
