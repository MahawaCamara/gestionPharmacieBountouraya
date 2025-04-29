# # Pharmacie/Produit/signals.py
# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
# from .models import Form

# @receiver(post_migrate)
# def init_forms(sender, **kwargs):
#     if sender.name == 'Pharmacie.Produit':
#         Form.objects.get_or_create(name="...")