# from django.shortcuts import redirect
# from django.urls import reverse

# class SuperuserRestrictionMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         path = request.path
#         user = request.user

#         # Liste des préfixes réservés aux utilisateurs simples
#         restricted_user_routes = [
#             '/pharmacien/',
#             '/produit/',
#             '/abonnement/',
#         ]

#         # Si superutilisateur et essaie d'accéder à une route utilisateur → bloqué
#         if user.is_authenticated and user.is_superuser:
#             if any(path.startswith(prefix) for prefix in restricted_user_routes):
#                 return redirect('home')

#         return self.get_response(request)
