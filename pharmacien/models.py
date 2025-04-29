from django.contrib.auth.models import User
from django.db import models

class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy')
    pharmacy_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    opening_hours = models.TextField()
    pharmacy_logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return self.pharmacy_name
