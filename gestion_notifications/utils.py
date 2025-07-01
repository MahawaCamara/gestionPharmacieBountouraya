# # gestion_notifications/utils.py

# from datetime import timedelta
# from django.utils import timezone
# from pharmacien.models import Pharmacy
# from .models import Notification
# from Produit.models import Product, ProductAvailability, SearchHistory  # Assure-toi que ce modèle existe 
# from django.contrib.auth.models import User


#
# def generer_notifications_recherches():
#     """
#     Parcourt l'historique des recherches et notifie chaque pharmacie
#     uniquement si elle ne possède pas le produit recherché.
#     """
#     for search in SearchHistory.objects.all():
#         try:
#             for pharmacy in Pharmacy.objects.all():
#                 # Vérifie si la pharmacie ne possède PAS ce produit recherché
#                 possede_produit = ProductAvailability.objects.filter(
#                     pharmacy=pharmacy,
#                     product__name__icontains=search.query
#                 ).exists()

#                 if not possede_produit:
#                     Notification.objects.get_or_create(
#                         user=pharmacy.user,
#                         pharmacy=pharmacy,
#                         type='produit_recherche',
#                         titre="Recherche de produit",
#                         message=f"Des utilisateurs ont recherché '{search.query}', que vous ne proposez pas.",
#                         lu=False
#                     )
#         except Exception as e:
#             print(f"Erreur dans génération notifications recherches : {e}")


# def notifier_admin_produits_expirés():
#     aujourd_hui = timezone.now().date()
#     produits_expirés = Product.objects.filter(date_expiration__lt=aujourd_hui, est_expire=False)

#     admin = User.objects.filter(is_staff=True).first()  # on suppose un seul admin

#     for produit in produits_expirés:
#         produit.est_expire = True  # marquer comme expiré pour ne pas répéter
#         produit.save()

#         Notification.objects.create(
#             user=admin,
#             titre="Produit expiré",
#             message=f"Le produit **{produit.nom}** de la pharmacie **{produit.pharmacy.pharmacy_name}** est expiré.",
#             lien=f"/admin/produits/{produit.id}/"  # lien vers une action ou info
#         )
        
# def generer_notifications_expiration():
#     """
#     Génère les notifications pour les produits arrivant à expiration sous 30 jours.
#     """
#     aujourd_hui = timezone.now().date()
#     seuil = aujourd_hui + timedelta(days=30)

#     produits_a_expirer = Product.objects.filter(date_expiration__lte=seuil)

#     for produit in produits_a_expirer:
#         pharmacie = produit.pharmacy  # ou .created_by selon votre modèle
#         user = getattr(pharmacie, 'user', None)

#         if user:
#             Notification.objects.get_or_create(
#                 user=user,
#                 pharmacy=pharmacie,
#                 type='expiration_produit',
#                 titre=f"Produit bientôt expiré : {produit.nom}",
#                 message=f"Le produit {produit.nom} expire le {produit.date_expiration.strftime('%d/%m/%Y')}",
#                 lu=False
#             )


# gestion_notifications/utils.py

from datetime import timedelta
from django.utils import timezone
from pharmacien.models import Pharmacy
from .models import Notification
from Produit.models import Product, ProductAvailability, SearchHistory
from users.models import User  # ton modèle personnalisé
from django.db.models import Q

# 🔔 Fonction 1 : notifier les pharmacies qui ne possèdent pas un produit recherché récemment
def generer_notifications_recherches():
    """
    Parcourt l'historique des recherches et notifie chaque pharmacie
    si elle ne possède pas le produit recherché.
    """
    maintenant = timezone.now()
    recherches = SearchHistory.objects.all()

    for search in recherches:
        produit_recherche = search.query.strip().lower()

        for pharmacie in Pharmacy.objects.all():
            user = getattr(pharmacie, 'user', None)
            if not user:
                continue

            # Vérifie si la pharmacie possède ce produit
            possede_produit = ProductAvailability.objects.filter(
                pharmacy=pharmacie,
                product__name__icontains=produit_recherche
            ).exists()

            # Si elle ne le possède pas, et pas déjà notifiée récemment
            if not possede_produit:
                notification_existante = Notification.objects.filter(
                    pharmacy=pharmacie,
                    user=user,
                    type='produit_recherche',
                    message__icontains=produit_recherche,
                    date_creation__gte=maintenant - timedelta(minutes=10)
                ).exists()

                if not notification_existante:
                    Notification.objects.create(
                        pharmacy=pharmacie,
                        user=user,
                        type='produit_recherche',
                        titre=f"Produit recherché : {produit_recherche}",
                        message=f"Des utilisateurs ont recherché '{produit_recherche}', que vous ne proposez pas.",
                        lu=False
                    )

# 🔔 Fonction 2 : notifier les pharmacies des produits bientôt expirés
def generer_notifications_expiration():
    """
    Notifie les pharmacies si un de leurs produits expire dans les 30 jours.
    """
    aujourd_hui = timezone.now().date()
    seuil = aujourd_hui + timedelta(days=30)

    produits = Product.objects.filter(
        date_expiration__lte=seuil,
        est_expire=False
    )

    for produit in produits:
        pharmacie = produit.pharmacy
        user = getattr(pharmacie, 'user', None)

        if user:
            Notification.objects.get_or_create(
                user=user,
                pharmacy=pharmacie,
                type='expiration_produit',
                titre=f"Produit bientôt expiré : {produit.nom}",
                message=f"Le produit {produit.nom} expire le {produit.date_expiration.strftime('%d/%m/%Y')}",
                lu=False
            )

# 🔔 Fonction 3 : notifier admin et pharmacien si un produit est déjà expiré
def verifier_produits_expire():
    """
    Vérifie les produits déjà expirés et notifie l'admin et le pharmacien concerné.
    """
    aujourd_hui = timezone.now().date()
    produits_expired = Product.objects.filter(date_expiration__lt=aujourd_hui, est_expire=False)

    for produit in produits_expired:
        produit.est_expire = True
        produit.save()

        content_type = produit.get_content_type()
        admin = User.objects.filter(is_staff=True).first()
        pharmacien_user = produit.created_by.user

        # Notification admin
        if admin:
            Notification.objects.create(
                user=admin,
                pharmacy=produit.pharmacy,
                type='expiration_produit',
                titre=f"Produit expiré : {produit.nom}",
                message=f"Le produit '{produit.nom}' de la pharmacie '{produit.pharmacy.pharmacy_name}' est expiré.",
                content_type=content_type,
                object_id=produit.id,
                lu=False
            )

        # Notification pharmacien
        if pharmacien_user:
            Notification.objects.create(
                user=pharmacien_user,
                pharmacy=produit.pharmacy,
                type='expiration_produit',
                titre=f"⚠️ Produit expiré : {produit.nom}",
                message=f"Votre produit '{produit.nom}' est expiré depuis le {produit.date_expiration}.",
                content_type=content_type,
                object_id=produit.id,
                lu=False
            )
            
from django.contrib.auth import get_user_model       # Pour obtenir le modèle User de Django

User = get_user_model() # Récupère le modèle d'utilisateur actif (django.contrib.auth.models.User ou votre CustomUser)

def notifier_pharmacies_non_possedant_produit(nom_produit_recherche):
    """
    Notifie les pharmaciens si un produit recherché par un utilisateur n'est pas en stock chez eux,
    ou si le produit n'existe pas du tout dans la base de données globale.
    """
    maintenant = timezone.now()
    
    # 1. Identifier les produits qui correspondent au nom recherché
    # Ceci trouve tous les IDs de produits dont le nom contient 'nom_produit_recherche'.
    produits_correspondants_ids = Product.objects.filter(
        name__icontains=nom_produit_recherche
    ).values_list('id', flat=True)

    # 2. Récupérer toutes les pharmacies approuvées et associées à un utilisateur
    # On filtre ici pour ne considérer que les pharmacies valides pour les notifications.
    pharmacies_eligible_a_notifier = Pharmacy.objects.filter(
        is_approved=True, 
        user__isnull=False # S'assure que la pharmacie est liée à un utilisateur Django
    )

    if not produits_correspondants_ids:
        # Cas 1: Le produit recherché n'existe PAS DU TOUT dans la base de données Product.
        # Notifier TOUTES les pharmacies éligibles de cette nouvelle demande.
        pharmacies_a_notifier_ce_tour = pharmacies_eligible_a_notifier
        notification_titre = f"Nouvelle demande : '{nom_produit_recherche}'"
        notification_message = f"Un produit très recherché, '{nom_produit_recherche}', n'est actuellement pas répertorié. Pensez à l'ajouter et/ou à le stocker si pertinent."
    else:
        # Cas 2: Le produit existe dans la base de données Product.
        # Identifier les pharmacies qui POSSÈDENT AU MOINS UN de ces produits.
        pharmacies_ayant_produit_ids = ProductAvailability.objects.filter(
            product__id__in=produits_correspondants_ids,
            pharmacy__in=pharmacies_eligible_a_notifier # Limite la recherche aux pharmacies éligibles
        ).values_list('pharmacy__id', flat=True).distinct()

        # Pharmacies à notifier = Pharmacies éligibles - Pharmacies qui ont le produit.
        pharmacies_a_notifier_ce_tour = pharmacies_eligible_a_notifier.exclude(
            id__in=pharmacies_ayant_produit_ids
        )
        notification_titre = f"Produit recherché: '{nom_produit_recherche}'"
        notification_message = f"Des utilisateurs recherchent '{nom_produit_recherche}', produit que vous ne possédez pas. Pensez à le vérifier ou à l'ajouter à votre stock."

    # 3. Créer des notifications pour les pharmacies identifiées, en évitant le spam
    notification_type_code = 'produit_recherche'

    for pharmacie in pharmacies_a_notifier_ce_tour:
        user_destinataire = pharmacie.user # Récupère l'objet User lié à la pharmacie

        # Vérification anti-spam : Cherche si une notification similaire (même type, même produit)
        # a déjà été envoyée à cette pharmacie/utilisateur récemment.
        # On utilise ici les champs 'pharmacy', 'user', 'type', 'message__icontains' et 'date_creation'.
        recent_notification_exists = Notification.objects.filter(
            pharmacy=pharmacie,
            user=user_destinataire,
            type=notification_type_code,
            message__icontains=nom_produit_recherche, # Vérifie que la requête de recherche est dans le message
            date_creation__gte=maintenant - timedelta(days=1) # Pas plus d'une fois par jour
        ).exists()

        if not recent_notification_exists:
            # Création de la notification si aucune récente n'existe
            Notification.objects.create(
                pharmacy=pharmacie,        # Le champ ForeignKey vers Pharmacy
                user=user_destinataire,    # Le champ ForeignKey vers User
                type=notification_type_code,
                titre=notification_titre,
                message=notification_message,
                lu=False, # Par défaut non lue
                # date_creation est auto_now_add=True
                # created_at est auto_now_add=True (vous pourriez vouloir en supprimer un)
            )
