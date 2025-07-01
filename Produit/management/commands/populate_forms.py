from django.core.management.base import BaseCommand
from Produit.models import Form

class Command(BaseCommand):
    help = "Ajoute les formes pharmaceutiques par défaut"

    def handle(self, *args, **kwargs):
        default_forms = [
            "Comprimé",
            "Gélule",
            "Sirop",
            "Pommade",
            "Injection",
            "Suppositoire",
            "Crème",
            "Solution buvable",
            "Spray",
            "Patch",
        ]

        for name in default_forms:
            obj, created = Form.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ajouté : {name}"))
            else:
                self.stdout.write(f"Déjà existant : {name}")
