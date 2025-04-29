# from django.db import models
# from django.contrib.auth.models import User

# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     type = models.CharField(max_length=100)
#     description = models.TextField()
#     expiration_date = models.DateField()
#     usage_mode = models.TextField()
#     posology = models.TextField()
#     forms = models.ManyToManyField(Form, through='ProductAvailability')

#     def __str__(self):
#         return self.name

# class ProductAvailability(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     pharmacy = models.ForeignKey(User, on_delete=models.CASCADE)
#     form = models.ForeignKey(Form, on_delete=models.CASCADE)
#     dosage = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.product.name} - {self.form.name} - {self.dosage} - {self.price} FNG"


from django.db import models
from django.contrib.auth.models import User

class Form(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField()
    expiration_date = models.DateField()
    usage_mode = models.TextField()
    posology = models.TextField()

    def __str__(self):
        return self.name

class ProductAvailability(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='availabilities')
    pharmacy = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey('Form', on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)  # <-- Nouveau champ dosage
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.form.name} - {self.dosage} - {self.price} FNG"

class SearchHistory(models.Model):
    session_id = models.CharField(max_length=255, null=True, blank=True)  # ID de session pour non-authentifiés
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"