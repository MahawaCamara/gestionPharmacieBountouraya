from django.shortcuts import redirect
from django.utils import timezone
from abonnement.models import Abonnement
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
from datetime import date, timedelta

# class VerifierAbonnementMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated and hasattr(request.user, 'pharmacy'):
#             abonnement = getattr(request.user, 'abonnement', None)
#             if abonnement:
#                 if abonnement.periode_essai and abonnement.date_expiration < timezone.now():
#                     abonnement.est_actif = False
#                     abonnement.save()
#                     return redirect('abonnement:choix_mode_paiement')
#         return self.get_response(request)

# from django.shortcuts import redirect
# from django.utils import timezone
# from django.utils.deprecation import MiddlewareMixin
# from django.urls import reverse
# from datetime import timedelta

class AbonnementMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user

        if not user.is_authenticated or user.is_superuser:
            return None

        # 🌐 Liste des routes protégées (à adapter selon ton projet)
        protected_prefixes = [
            '/gestion_notifications/',
            '/Produit/',
            '/pharmacien/',
        ]

        # ✅ Ne rien faire si route non protégée
        if not any(request.path.startswith(prefix) for prefix in protected_prefixes):
            return None

        # 🔄 URL redirection vers la page d'abonnement
        abonnement_url = reverse('abonnement:choix_mode_paiement')
        if request.path == abonnement_url:
            return None

        # Récupération de l’abonnement
        abonnement = getattr(user, 'abonnement', None)

        # Blocage si abonnement manquant ou expiré
        if not abonnement or not abonnement.est_actif:
            return redirect(abonnement_url)

        # Blocage si date d’expiration dépassée
        if abonnement.date_expiration and timezone.now() > abonnement.date_expiration:
            abonnement.est_actif = False
            abonnement.save()
            return redirect(abonnement_url)

        return None