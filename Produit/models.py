from django.utils import timezone;
from django.db import models;
from django.contrib.auth.models import User
from pharmacien.models import Pharmacy;

#### Model de la forme pharmaceutiques #####
class Form(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ajout de unique=True pour éviter les doublons
    
    # Déclaration explicite du manager
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Forme pharmaceutique"
        verbose_name_plural = "Formes pharmaceutiques"

    def __str__(self):
        return self.name
##### Model du produit
class Product(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField()
    expiration_date = models.DateField()
    usage_mode = models.TextField()
    posology = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # Ajout du champ image
    created_by = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)  # 👈 Ajouté
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    est_expire = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

###  Model de la disponibilité produit ####
class ProductAvailability(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='availabilities')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)  # <-- Nouveau champ dosage
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product.name} - {self.form.name} - {self.dosage} - {self.price} FNG"

#### Model de l'historique des recherches ####
class SearchHistory(models.Model):
    # ID de session pour les utilisateurs non authentifiés, ajout de db_index pour la performance
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
