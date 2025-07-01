from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from Produit.models import Product, ProductAvailability
from gestion_notifications.models import Notification
from interfaceUtilisateur.forms import ContactPharmacienForm
from django.shortcuts import get_object_or_404, render
from Produit.models import Product, SearchHistory  
from gestion_notifications.models import Message, Pharmacy 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string 
from django.urls import reverse 
from django.contrib import messages as dj_messages 
from django.contrib.auth import get_user_model

User = get_user_model()
def group_by_six(lst):
    return [lst[i:i + 6] for i in range(0, len(lst), 6)]

def index(request):
     # Formulaire de contact (inchangé)...

    # Stats dynamiques
    total_pharmacies = Pharmacy.objects.count()
    total_produits = Product.objects.count()
    total_recherches = SearchHistory.objects.count()

    # Tu peux personnaliser ce nombre si tu veux le gérer autrement
    total_visiteurs = 125  # optionnel : nombre fixe ou calculé si tu ajoutes un modèle "Visiteur"

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        full_message = f"Nom: {name}\nEmail: {email}\n\nMessage:\n{message_text}"

        try:
            # Envoi email
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_RECEIVER_EMAIL],
                fail_silently=False,
            )
            admin_user = User.objects.filter(is_staff=True).first()

            if admin_user:
                Message.objects.create(
                    expediteur_nom=name,
                    expediteur_email=email,
                    destinataire=admin_user,
                    sujet=subject,
                    corps=message_text,
                    est_lu=False
                )

            dj_messages.success(request, "Merci pour votre message, nous vous répondrons bientôt.")
        except Exception as e:
            print(e)
            dj_messages.error(request, "Erreur lors de l'envoi. Réessayez.")

        return redirect('/#contact')

    # Partie GET (affichage de la page d’accueil)
    recent_availabilities = ProductAvailability.objects.select_related('product', 'pharmacy', 'form').order_by('-id')[:18]
    grouped_availabilities = group_by_six(list(recent_availabilities))

    types = Product.objects.values_list('type', flat=True).distinct()
    villes = Pharmacy.objects.values_list('address', flat=True).distinct()

    return render(request, 'interfaceUtilisateur/pages/index.html', {
        'grouped_availabilities': grouped_availabilities, 
        'types': types,
        'villes': villes,
        'total_pharmacies': total_pharmacies,
        'total_produits': total_produits,
        'total_recherches': total_recherches,
        'total_visiteurs': total_visiteurs,
    })

# Vue pour la gestion du lien nous rejoindre
def rejoindre(request):
    if request.user.is_authenticated:
        # ✅ Rediriger le superuser en priorité
        if request.user.is_superuser:
            return redirect('administration:dashboard_admin')

        # ✅ Ensuite vérifier si l'utilisateur est un pharmacien
        elif hasattr(request.user, 'pharmacy'):
            return redirect('pharmacien:dashboard')

        # ✅ Tous les autres utilisateurs
        else:
            return redirect('abonnement:page_abonnement')

    # ✅ Utilisateur non connecté
    return redirect('login')

##### Vue pour les details des produits côté interfaceUtilisateur #######
def public_product_details(request, id):
    product = get_object_or_404(Product, id=id)
    form = ContactPharmacienForm()

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ContactPharmacienForm(request.POST)
        if form.is_valid():
            nom_expediteur = form.cleaned_data['nom']
            email_expediteur = form.cleaned_data['email']
            message_corps = form.cleaned_data['message']

            pharmacie = product.created_by  # Pharmacy
            pharmacien_user = getattr(pharmacie, 'user', None)
            email_pharmacien = getattr(pharmacie, 'email', None)  # email propre à la pharmacie

            if not pharmacien_user or not email_pharmacien:
                return JsonResponse({
                    'status': 'error',
                    'message': "Pharmacien ou email de la pharmacie non trouvés."
                }, status=400)

            # Enregistrer le message en base
            Message.objects.create(
                expediteur_nom=nom_expediteur,
                expediteur_email=email_expediteur,
                destinataire=pharmacien_user,
                destinataire_pharmacy=pharmacie,
                sujet=f"Message de {nom_expediteur} concernant votre produit : {product.name}",
                corps=message_corps,
                est_lu=False
            )

            # Envoyer l'email à l'adresse de la pharmacie
            try:
                email_subject = f"Nouveau message de {nom_expediteur} - Produit : {product.name}"
                email_body = render_to_string('pharmacien/messages/nouveau_message_pharmacien.html', {
                    'expediteur_nom': nom_expediteur,
                    'expediteur_email': email_expediteur,
                    'sujet': f"Concernant : {product.name}",
                    'corps': message_corps,
                    'inbox_url': request.build_absolute_uri(reverse('gestion_notifications:pharmacien_boite_reception'))
                })

                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email_pharmacien],  # <-- ici, l'email de la pharmacie !
                    html_message=email_body
                )
            except Exception as e:
                return JsonResponse({
                    'status': 'warning',
                    'message': f'Message enregistré, mais erreur lors de l\'envoi de l\'email : {e}'
                })

            return JsonResponse({
                'status': 'success',
                'message': 'Message envoyé avec succès au pharmacien.'
            })
        print(request.POST)
        return JsonResponse({'status': 'error', 'message': dict(form.errors)}, status=400)

    return render(request, 'interfaceUtilisateur/pages/public_product_details.html', {
        'product': product,
        'form': form
    })

# Nouvelle vue pour enregistrer les recherches et notifier les pharmacies
@require_POST
def record_search_and_notify_pharmacy(request):
    query = request.POST.get('query')
    if query:
        # Enregistrer l'historique de recherche pour les utilisateurs non authentifiés (via session_id)
        session_id = request.session.session_key
        if not session_id: # Crée une session si elle n'existe pas
            request.session.save()
            session_id = request.session.session_key
        SearchHistory.objects.create(session_id=session_id, query=query)

        # Trouver les produits correspondant à la requête et notifier leurs pharmaciens
        matching_products = Product.objects.filter(name__icontains=query)

        for product in matching_products:
            if hasattr(product, 'created_by') and product.created_by and product.created_by.user:
                pharm_user = product.created_by.user
                # Créer une notification si elle n'existe pas déjà pour cette recherche et cet utilisateur
                Notification.objects.get_or_create(
                    user=pharm_user,
                    message=f"Un utilisateur a recherché le produit '{query}' que votre pharmacie propose.",
                    defaults={'is_read': False}
                )
        return JsonResponse({'status': 'success', 'message': 'Recherche enregistrée et pharmacies notifiées.'})
    return JsonResponse({'status': 'error', 'message': 'Requête invalide.'}, status=400)

### Vue pour d'affichage si la route n'existe pas #####
def custom_404_view(request):
    return render(request, "interfaceUtilisateur/404.html", status=404)