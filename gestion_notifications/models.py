from django.db import models
from django.conf import settings  # ✅ Bon
from pharmacien.models import Pharmacy # Assurez-vous que ces modèles existent
from Produit.models import Product
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

#### Model de la messengerie ####
class Message(models.Model):
    expediteur_nom = models.CharField(max_length=255)
    expediteur_email = models.EmailField()
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_recus'
    )
    destinataire_pharmacy = models.ForeignKey(
        Pharmacy, null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='messages_recus_pharmacie'
    )
    sujet = models.CharField(max_length=255)
    corps = models.TextField()
    date_envoye = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return f"De: {self.expediteur_nom} à: {self.destinataire.email} - Sujet: {self.sujet}"

#### Model de la notification ####
class Notification(models.Model):
    TYPE_CHOICES = [
        ('produit_recherche', 'Recherche de produit'),
        ('expiration_produit', 'Expiration de produit'),
        ('clic_fiche', 'Clic sur une fiche'),
        ('suggestion', 'Suggestion de produit'),
        # Ajoutez d'autres types si nécessaire
    ]
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=255)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def get_icon(self):
        return {
            'expiration_produit': 'fas fa-exclamation-triangle text-danger',
            'suggestion': 'fas fa-user-shield text-warning',
            'produit_recherche': 'fas fa-search text-primary',
            'clic_fiche': 'fas fa-hand-pointer text-success',
        }.get(self.type, 'fas fa-bell')

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.user.username}"

    