from django.conf import settings  # ✅ Bon
from django.contrib.auth import get_user_model
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from abonnement.models import Abonnement

### Model de la pharmacie ###
class Pharmacy(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pharmacy')
    pharmacy_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    opening_hours = models.TextField()
    pharmacy_logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    date_essai = models.DateTimeField(default=timezone.now)  # Ajouté
    abonnement_actif = models.BooleanField(default=False)    # Ajouté

    def est_en_essai(self):
        return timezone.now() < self.date_essai + timedelta(days=30)

    def doit_s_abonner(self):
        try:
            abonnement = self.user.abonnement
            # On vérifie si l'abonnement est valide (actif + non expiré)
            if abonnement.est_valide:
                return False
            return True
        except Abonnement.DoesNotExist:
            # Pas d'abonnement du tout, donc doit s'abonner
            return True

    def __str__(self):
        return self.pharmacy_name

    class Meta:
        verbose_name_plural = "Pharmacies"




User = get_user_model()

### Model de l'envoie de la reponse messagerie ###
class PendingSensitiveChange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_email = models.EmailField()
    new_password = models.CharField(max_length=255)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)  # ⏰ valable 2 minutes

    def __str__(self):
        return f"Changement en attente pour {self.user.username}"