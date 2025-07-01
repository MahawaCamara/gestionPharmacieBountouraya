# abonnement/context_processors.py
from abonnement.models import Abonnement
from django.utils import timezone
from datetime import datetime, timedelta

def abonnement_notification(request):
    if request.user.is_authenticated and hasattr(request.user, 'abonnement'):
        abonnement = request.user.abonnement

        if abonnement.date_expiration and abonnement.date_expiration > timezone.now():
            delta = abonnement.date_expiration - timezone.now()
            jours_restants = delta.days
            heures = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60

            print(f"[DEBUG] jours_restants = {jours_restants}")  # à supprimer après test

            if 0 <= jours_restants <= 29:
                return {
                    'jours_restants': jours_restants,
                    'heures_restantes': heures,
                    'minutes_restantes': minutes,
                }

    return {}
