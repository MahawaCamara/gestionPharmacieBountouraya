from django.core.management.base import BaseCommand
from abonnement.models import Formule

class Command(BaseCommand):
    help = "Créer des formules d'abonnement par défaut"

    def handle(self, *args, **kwargs):
        formules = [
            {"nom": "Basique", "duree_jours": 30, "prix": 10000},
            {"nom": "Pro", "duree_jours": 365, "prix": 100000},
            # Ajoute d'autres formules si besoin
        ]

        for f in formules:
            formule_obj, created = Formule.objects.get_or_create(
                nom=f["nom"],
                defaults={"duree_jours": f["duree_jours"], "prix": f["prix"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Formule '{f['nom']}' créée"))
            else:
                self.stdout.write(f"Formule '{f['nom']}' existe déjà")

        self.stdout.write(self.style.SUCCESS("Initialisation des formules terminée."))
