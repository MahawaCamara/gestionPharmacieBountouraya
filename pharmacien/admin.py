# Register your models here.
from django.contrib import admin
from .models import Pharmacy

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('pharmacy_name', 'address', 'phone_number', 'email', 'is_approved')
    search_fields = ('pharmacy_name', 'email')
    list_filter = ('is_approved',)
