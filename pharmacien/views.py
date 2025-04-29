from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
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
from .forms import CustomLoginForm, CustomSetPasswordForm, CustomUserCreationForm, PharmacyForm, UpdateEmailForm
from .models import Pharmacy


@login_required
def dashboard(request):
    # Vérifiez si l'utilisateur a une pharmacie associée
    if not hasattr(request.user, 'pharmacy'):
        return redirect('pharmacien:pharmacy_registration')  # Redirigez l'utilisateur vers l'enregistrement de la pharmacie

    # Si l'utilisateur a une pharmacie, vous pouvez afficher des informations pertinentes dans le tableau de bord
    return render(request, 'administration/pages/dashboard.html')

#vue pour la connexion
def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)

            remember_me = request.POST.get("remember_me") == "on"
            if remember_me:
                # Session dure 7 jours (en secondes)
                request.session.set_expiry(7 * 24 * 60 * 60)
            else:
                # Session supprimée à la fermeture du navigateur
                request.session.set_expiry(0)

            return redirect("pharmacien:dashboard")  # Redirige vers ton dashboard ou accueil
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = CustomLoginForm()
    form = CustomLoginForm()
    return render(request, "administration/pages/account/login.html", {"form": form})

#vue pour la création d'un compte
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre compte a été créé avec succès!")
            return redirect('pharmacien:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'administration/pages/account/signup.html', {'form': form})

#vue pour l'envoi d'un lien lien de modification de mot de pass dans son compte gmail
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Ici on omet l'envoi de l'email
            messages.success(request, "Si un compte existe pour cet email, un lien de réinitialisation a été envoyé.")
            return redirect('pharmacien:password_reset_done')
    else:
        form = PasswordResetForm()
    form = PasswordResetForm()
    return render(request, 'administration/pages/account/password_reset.html', {'form': form})

# Vue pour définir un nouveau mot de passe
def password_reset_confirm(request, uidb64, token):
    if request.method == "POST":
        form = CustomSetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre mot de passe a été mis à jour.")
            return redirect('pharmacien:login')
    else:
        form = CustomSetPasswordForm(user=request.user)
    return render(request, 'administration/pages/account/password_reset_confirm.html', {'form': form})

def password_reset_done(request):
    return render(request, 'administration/pages/account/password_reset_done.html')


#Enregistrement d'une pharmacie
@login_required
def pharmacy_registration(request):
    # Vérifiez si l'utilisateur a déjà une pharmacie associée
    if hasattr(request.user, 'pharmacy'):
        return redirect('pharmacien:dashboard')  # L'utilisateur a déjà une pharmacie, redirigez vers le tableau de bord

    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES)
        if form.is_valid():
            # Créez la pharmacie associée à l'utilisateur
            pharmacy = form.save(commit=False)
            pharmacy.user = request.user
            pharmacy.save()
            # Message de succès
            messages.success(request, "Votre pharmacie a été enregistrée avec succès!")
            return redirect('pharmacien:dashboard')  # Redirigez l'utilisateur après l'enregistrement
        else:
            # Message d'erreur si le formulaire est invalide
            messages.error(request, "Une erreur s'est produite. Veuillez vérifier les informations et réessayer.")
    else:
        form = PharmacyForm()

    return render(request, 'administration/pages/pharmacy_registration.html', {'form': form})

# vue pour recuperer et modifier les informations de la pharmacie `
@login_required
def my_pharmacy(request):
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
    
    return render(request, 'administration/pages/my_pharmacy.html', {'form': form, 'pharmacy': pharmacy})


#vue pour le profile
@login_required
def profile(request):
    """Affiche la page de profil de l'utilisateur connecté."""
    return render(request, 'administration/pages/pharmacie/profile.html', {'user': request.user})

#vue pour modifier l'email de l'utilisateur connecté
@login_required
def update_email(request):
    if request.method == 'POST':
        form = UpdateEmailForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre adresse email a été mise à jour avec succès.')
            return redirect('pharmacien:profile')
        else:
            messages.error(request, 'Il y a eu une erreur lors de la mise à jour de votre email.')
    else:
        form = UpdateEmailForm(user=request.user)
    return render(request, 'administration/pages/pharmacie/update_email.html', {'form': form})


#vue pour modifier le mot de pass de l'utilisateur connecté
@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('pharmacien:profile')
        else:
            messages.error(request, 'Il y a eu une erreur lors de la mise à jour de votre mot de passe.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'administration/pages/pharmacie/update_password.html', {'form': form})