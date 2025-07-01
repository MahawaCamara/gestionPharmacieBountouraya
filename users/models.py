from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from abonnement.models import Abonnement
from pharmacien.models import Pharmacy

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire!")

        if not password:
            raise ValueError("Le mot de passe est obligatoire")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire!")

        if not password:
            raise ValueError("Le mot de passe est obligatoire")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    is_confirmed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255,blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

     # Ajouter des relations 'related_name' pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group', related_name='custom_user_groups', blank=True
        )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='custom_user_permissions', blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

