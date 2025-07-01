#### Mes importations ####
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str  
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from requests import request
from Produit.models import Form, Product, SearchHistory
from abonnement.context_processors import abonnement_notification
from abonnement.models import Abonnement
from .forms import CustomLoginForm, CustomSetPasswordForm, CustomUserCreationForm,  PharmacyForm, SensitiveChangeForm, UpdateEmailForm
from .models import PendingSensitiveChange, Pharmacy
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  # ✅ Bon
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from gestion_notifications.models import Notification

#### Vue pour afficher le dashboard de la pharmacie #####
@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    pharmacie = request.user.pharmacy

    # Statistiques spécifiques à la pharmacie
    total_produits = Product.objects.filter(created_by=pharmacie).count()
    total_types_produits = Product.objects.filter(created_by=pharmacie).values('type').distinct().count()
    total_recherches = SearchHistory.objects.filter(
        query__in=Product.objects.filter(created_by=pharmacie).values_list('name', flat=True)
    ).count()

    return render(request, 'administration/pages/dashboard.html', {
        'pharmacie': pharmacie,
        'total_produits': total_produits,
        'total_types_produits': total_types_produits,
        'total_recherches': total_recherches,
    })

    # Statistiques dynamiques
    total_produits = Product.objects.count()
    total_types_produits = Form.objects.count()
    total_recherches = SearchHistory.objects.count()

    # Abonnement (tu peux adapter selon ta logique)
    abonnement = Abonnement.objects.filter(user=request.user).order_by('-date_debut').first()

    temps_restant = None
    heures = 0
    minutes = 0

    if abonnement and abonnement.est_actif and abonnement.periode_essai:
        date_fin = abonnement.date_debut + timedelta(days=abonnement.formule.duree_mois * 30)  # approximation
        temps_restant = date_fin - timezone.now()

        if temps_restant.total_seconds() > 0:
            total_sec = int(temps_restant.total_seconds())
            heures = (total_sec // 3600) % 24
            minutes = (total_sec // 60) % 60

    notifications = Notification.objects.filter(user=request.user).order_by('-date_creation')[:10]

    return render(request, 'administration/pages/dashboard.html', {
        'pharmacie': pharmacie,
        'temps_restant': temps_restant,
        'heures': heures,
        'minutes': minutes,
        'notifications': notifications,
        'total_produits': total_produits,
        'total_types_produits': total_types_produits,
        'total_recherches': total_recherches,
    })

#Enregistrement d'une pharmacie
@login_required
def pharmacy_registration(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    if hasattr(request.user, 'pharmacy'):
        return redirect('pharmacien:dashboard')

    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES)
        if form.is_valid():
            
            pharmacy = form.save(commit=False)
            pharmacy.user = request.user
            pharmacy.latitude = form.cleaned_data.get('latitude')
            pharmacy.longitude = form.cleaned_data.get('longitude')
            pharmacy.date_essai = timezone.now()  # Ajout automatique
            pharmacy.abonnement_actif = False      # Par défaut
            pharmacy.save()

            messages.success(request, "✅ Votre pharmacie a été enregistrée avec succès. Vous bénéficiez d'un essai gratuit d'un mois.")
            return redirect('pharmacien:dashboard')
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PharmacyForm()

    return render(request, 'administration/pages/pharmacie/pharmacy_registration.html', {'form': form})

# vue pour recuperer et modifier les informations de la pharmacie `
@login_required
def my_pharmacy(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
     # Récupérer la pharmacie de l'utilisateur connecté
    pharmacy = Pharmacy.objects.get(user=request.user)

    # Initialiser le formulaire avec les données de la pharmacie
    form = PharmacyForm(instance=pharmacy)

    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES, instance=pharmacy)
        if form.is_valid():
            form.save()
            # Rediriger ou afficher un message de succès ici
            messages.success(request, 'La modification a été bien effectuer')
            return redirect('pharmacien:dashboard')
    
    return render(request, 'administration/pages/pharmacie/my_pharmacy.html', {'form': form, 'pharmacy': pharmacy})

#vue pour le profile
@login_required
def profile(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    """Affiche la page de profil de l'utilisateur connecté."""
    return render(request, 'administration/pages/pharmacie/profile.html', {'user': request.user})

#### Vue pour envoie du lien et le code de validation #####
@login_required
def sensitive_change_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        code = get_random_string(length=6, allowed_chars='0123456789')

        pending = PendingSensitiveChange.objects.create(
            user=request.user,
            new_email=email,
            new_password=make_password(password),
            code=code
        )

        send_mail(
            subject="Code de confirmation - PharmaConnect",
            message=f"Bonjour {request.user.username},\n\nVotre code de confirmation est : {code}\nIl est valable 10 minutes.",
            from_email="no-reply@pharmaconnect.com",
            recipient_list=[email],
        )

        messages.success(request, "Un code a été envoyé à votre nouvelle adresse email.")
        return redirect('pharmacien:verify_sensitive_code')

    return render(request, 'administration/pages/pharmacie/sensitive_change_form.html')

##### Vue pour la confirmation de la modification ######
def confirm_sensitive_change(request, token):
    try:
        pending = PendingSensitiveChange.objects.get(token=token, is_confirmed=False)
    except PendingSensitiveChange.DoesNotExist:
        return HttpResponseForbidden("Lien invalide ou déjà utilisé.")

    user = pending.user

    # Appliquer les changements
    if pending.new_email:
        user.email = pending.new_email
    if pending.new_password:
        user.password = pending.new_password

    user.save()
    pending.is_confirmed = True
    pending.save()

    messages.success(request, "Vos informations ont été modifiées avec succès.")
    return redirect('pharmacien:profile')

##### Vue pour verifier le code de validation ######
@login_required
def verify_sensitive_code(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        try:
            pending = PendingSensitiveChange.objects.get(user=request.user, is_confirmed=False)
        except PendingSensitiveChange.DoesNotExist:
            messages.error(request, "Aucune demande en attente.")
            return redirect('pharmacien:profile')

        if pending.is_expired():
            pending.delete()
            messages.error(request, "Le code a expiré. Veuillez recommencer.")
            return redirect('pharmacien:sensitive_change_form')

        if pending.code != input_code:
            messages.error(request, "Code incorrect.")
            return redirect('pharmacien:verify_sensitive_code')

        # Appliquer les changements
        user = request.user
        user.email = pending.new_email
        user.password = pending.new_password
        user.save()

        pending.is_confirmed = True
        pending.save()

        messages.success(request, "Vos informations ont été modifiées avec succès.")
        return redirect('pharmacien:profile')

    return render(request, 'administration/pages/pharmacie/verify_code.html')
