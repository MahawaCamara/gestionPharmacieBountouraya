##### Mes importations ########
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from gestion_notifications.models import Notification
from .forms import LoginForm, RegisterForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

##### Vue pour se connecter connexion ######
def custom_login_view(request):
    # ✅ Si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        # On redirige en priorité le superuser
        if request.user.is_superuser:
            return redirect('administration:dashboard_admin')
        # Ensuite les pharmaciens
        elif hasattr(request.user, 'pharmacy'):
            return redirect('pharmacien:dashboard')
        # Puis les utilisateurs simples
        else:
            return redirect('abonnement:page_abonnement')

    # Traitement du formulaire de connexion
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            remember = form.cleaned_data["remember_me"]

            user = User.objects.filter(email=email).first()

            # Vérifier si le compte est bloqué
            if user and not user.is_active:
                form.add_error(None, "🚫 Votre compte a été bloqué. Veuillez contacter l'administrateur.")
                return render(request, "user/login.html", {"form": form})

            # Authentification
            user_auth = authenticate(request, email=email, password=password)
            if user_auth is not None:
                login(request, user_auth)

                # Gérer la durée de session selon la case "se souvenir de moi"
                if not remember:
                    request.session.set_expiry(0)  # expire à la fermeture du navigateur
                else:
                    request.session.set_expiry(60 * 60 * 24 * 7)  # 1 semaine

                # ✅ Redirections après login selon le type d'utilisateur
                if user_auth.is_superuser:
                    return redirect('administration:dashboard_admin')
                elif hasattr(user_auth, 'pharmacy'):
                    return redirect('pharmacien:dashboard')
                else:
                    return redirect('abonnement:page_abonnement')

            # Sinon, email ou mot de passe incorrect
            form.add_error(None, "Email ou mot de passe invalide.")
    else:
        form = LoginForm()

    return render(request, "user/login.html", {"form": form})


##### Vue pour se connecter deconnecter ######
def custom_logout_view(request):
    logout(request)
    next_url = request.GET.get('next', 'home')  # ou 'rejoindre', selon ce que tu veux
    return redirect(next_url)


##### Vue pour s'inscrire ######
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte créé avec succès. Vous pouvez vous connecter.")
            return redirect("login")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()
    return render(request, "user/register.html", {"form": form})