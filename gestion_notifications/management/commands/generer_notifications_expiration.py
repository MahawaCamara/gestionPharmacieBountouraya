# from django.utils import timezone
# from django.contrib.contenttypes.models import ContentType
# from Produit.models import Product
# from gestion_notifications.models import Notification
# from users.models import User

# def verifier_produits_expire():
#     aujourd_hui = timezone.now().date()
#     produits_expired = Product.objects.filter(expiration_date__lt=aujourd_hui, est_expire=False)

#     for produit in produits_expired:
#         produit.est_expire = True  # Marquer comme traité
#         produit.save()

#         Notification.objects.create(
#             type='expiration_produit',
#             user=User.objects.filter(is_staff=True).first(),  # ou broadcast à tous les admins
#             pharmacy=produit.created_by,
#             titre=f"Produit expiré : {produit.name}",
#             message=f"Le produit '{produit.name}' de la pharmacie '{produit.created_by.pharmacy_name}' est expiré.",
#             content_type=ContentType.objects.get_for_model(produit),
#             object_id=produit.id,
#             lu=False,
#         )


from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from Produit.models import Product
from gestion_notifications.models import Notification
from users.models import User

def verifier_produits_expire():
    aujourd_hui = timezone.now().date()
    produits_expired = Product.objects.filter(expiration_date__lt=aujourd_hui, est_expire=False)

    for produit in produits_expired:
        produit.est_expire = True  # Marquer comme expiré
        produit.save()

        # Récupération des acteurs
        admin = User.objects.filter(is_staff=True).first()
        pharmacien_user = produit.created_by.user  # ✅ ici on passe bien un User, pas une Pharmacy
        content_type = ContentType.objects.get_for_model(produit)

        # Notification à l'admin
        if admin:
            Notification.objects.create(
                type='expiration_produit',
                user=admin,
                pharmacy=produit.created_by,
                titre=f"Produit expiré : {produit.name}",
                message=f"Le produit '{produit.name}' de la pharmacie '{produit.created_by.pharmacy_name}' est expiré.",
                content_type=content_type,
                object_id=produit.id,
                lu=False,
            )

        # Notification au pharmacien (lui-même)
        Notification.objects.create(
            type='expiration_produit',
            user=pharmacien_user,
            pharmacy=produit.created_by,
            titre=f"⚠️ Produit expiré : {produit.name}",
            message=f"Votre produit '{produit.name}' est expiré depuis le {produit.expiration_date}. Veuillez le retirer rapidement.",
            content_type=content_type,
            object_id=produit.id,
            lu=False,
        )