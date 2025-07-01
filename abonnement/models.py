from django.conf import settings
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta

#### Model de la formule ####
class Formule(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    duree_mois = models.PositiveIntegerField(help_text="Durée de l'abonnement en mois")
    prix = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix en GNF")

    def __str__(self):
        return f"{self.nom} ({self.duree_mois} mois) - {self.prix} GNF"

#### Model de l'abonnement ####
class Abonnement(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    formule = models.ForeignKey(Formule, on_delete=models.PROTECT)
    est_actif = models.BooleanField(default=False)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    periode_essai = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.date_debut:
            self.date_debut = timezone.now()
        if not self.date_expiration:
            self.date_expiration = self.date_debut + relativedelta(months=self.formule.duree_mois)
            print(f"[DEBUG] date_expiration fixée à {self.date_expiration}")
        super().save(*args, **kwargs)
        
    @property
    def est_valide(self):
        if not self.est_actif:
            return False
        if self.date_expiration and timezone.now() > self.date_expiration:
            return False
        return True

    def __str__(self):
        return f"{self.user.email} - {self.formule.nom} - {'Actif' if self.est_actif else 'Inactif'}"
