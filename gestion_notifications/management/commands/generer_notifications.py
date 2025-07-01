from django.core.management.base import BaseCommand
from utils import generer_notifications_recherches, generer_notifications_expiration, verifier_produits_expire

class Command(BaseCommand):
    help = 'Génère toutes les notifications (recherche + expiration + expirés)'

    def handle(self, *args, **kwargs):
        generer_notifications_recherches()
        generer_notifications_expiration()
        verifier_produits_expire()
        self.stdout.write(self.style.SUCCESS('✅ Notifications générées avec succès.'))