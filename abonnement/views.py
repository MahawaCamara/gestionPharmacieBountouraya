#### Mes importations ####
from datetime import timedelta
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from pharmacien.models import Pharmacy
from .models import Abonnement, Formule
from django.utils import timezone

# Page d'information : inviter l'utilisateur à s'abonner s'il n'a pas encore d'abonnement actif
@login_required
def page_abonnement(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    if hasattr(request.user, 'abonnement'):
        messages.info(request, "Vous êtes déjà abonné.")
        return redirect('pharmacien:pharmacy_registration')
    return render(request, 'abonnement/page_abonnement.html')

# Essaie d'un mois de gratuité
@login_required
def essai_gratuit(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    """Attribue un essai gratuit de 30 jours à l'utilisateur connecté."""
    if hasattr(request.user, 'abonnement'):
        messages.info(request, "Vous êtes déjà abonné.")
        return redirect('pharmacien:pharmacy_registration')

    formule = Formule.objects.filter(nom="Standard").first()
    if not formule:
        messages.error(request, "La formule 'Standard' n'existe pas.")
        return redirect('abonnement:page_abonnement')

    Abonnement.objects.create(
        user=request.user,
        formule=formule,
        est_actif=True,
        date_debut=timezone.now(),
        periode_essai=True  # à condition que ce champ existe dans ton modèle
    )
    messages.success(request, "Votre essai gratuit de 30 jours a commencé !")
    return redirect('pharmacien:pharmacy_registration')

# Étape 1 : choix du mode de paiement (Orange Money ou Carte Bancaire)
@login_required
def choix_mode_paiement(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    return render(request, 'abonnement/choix_mode_paiement.html')

# Orange Money - Étape 1 : saisir le numéro de téléphone
@login_required
def orange_money_etape1(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if request.method == 'POST':
        numero = request.POST.get('numero')
        if not numero or len(numero) < 8:
            messages.error(request, "Veuillez saisir un numéro valide.")
            return redirect('abonnement:orange_money_etape1')
        # Stocker le numéro dans la session pour les étapes suivantes
        request.session['om_numero'] = numero
        return redirect('abonnement:orange_money_etape2')
    return render(request, 'abonnement/orange_money_etape1.html')

# Orange Money - Étape 2 : saisir le montant à payer
@login_required
def orange_money_etape2(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if 'om_numero' not in request.session:
        return redirect('abonnement:orange_money_etape1')

    if request.method == 'POST':
        montant = request.POST.get('montant')
        try:
            montant_val = float(montant)
            if montant_val != 100000:
                raise ValueError
        except:
            messages.error(request, "Veuillez saisir le montant exact de 100 000 GNF.")
            return redirect('abonnement:orange_money_etape2')

        # Stocker le montant dans la session
        request.session['om_montant'] = montant_val
        return redirect('abonnement:orange_money_etape3')

    return render(request, 'abonnement/orange_money_etape2.html')

# Orange Money - Étape 3 : saisie du code SMS reçu (simulé)
@login_required
def orange_money_etape3(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if 'om_numero' not in request.session or 'om_montant' not in request.session:
        return redirect('abonnement:orange_money_etape1')
    if request.method == 'POST':
        code = request.POST.get('code')
        if code != '1234':
            messages.error(request, "Code SMS incorrect.")
            return redirect('abonnement:orange_money_etape3')
        # Paiement validé, marquer comme payé
        request.session['om_paye'] = True
        return redirect('abonnement:orange_money_confirmation')
    return render(request, 'abonnement/orange_money_etape3.html')

# Orange Money - Étape finale : création de l'abonnement et confirmation
@login_required
def orange_money_confirmation(request):
    # Empêche les administrateurs d'accéder à cette vue
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")

    # Vérifie que le paiement a bien été effectué
    if not request.session.get('om_paye'):
        return redirect('abonnement:orange_money_etape1')

    # Récupération de la formule "Standard"
    formule = Formule.objects.filter(nom="Standard").first()
    if not formule:
        messages.error(request, "La formule 'Standard' n'existe pas.")
        return redirect('abonnement:choix_mode_paiement')

    try:
        abonnement = Abonnement.objects.get(user=request.user)
    except Abonnement.DoesNotExist:
        # Création manuelle si c’est la première fois
        abonnement = Abonnement.objects.create(
            user=request.user,
            formule=formule,
            est_actif=True,
            date_debut=timezone.now(),
            date_expiration=timezone.now() + relativedelta(months=formule.duree_mois),
            periode_essai=False
        )
    else:
        # Mise à jour si l’abonnement existait déjà
        abonnement.formule = formule
        abonnement.est_actif = True
        abonnement.date_debut = timezone.now()
        abonnement.date_expiration = timezone.now() + relativedelta(months=formule.duree_mois)
        abonnement.periode_essai = False
        abonnement.save()

    # Nettoyer les variables de session liées au paiement
    for k in ['om_numero', 'om_montant', 'om_paye']:
        request.session.pop(k, None)

    messages.success(request, "Paiement Orange Money réussi !")
    return redirect('pharmacien:pharmacy_registration')

# Carte Bancaire - Étape 1 : saisie du numéro de carte
@login_required
def carte_bancaire_etape1(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if request.method == 'POST':
        numero = request.POST.get('numero_carte')
        if not numero or len(numero) not in [18, 19]:
            messages.error(request, "Numéro de carte invalide.")
            return redirect('abonnement:carte_bancaire_etape1')
        request.session['cb_numero'] = numero
        return redirect('abonnement:carte_bancaire_etape2')
    return render(request, 'abonnement/carte_bancaire_etape1.html')

# Carte Bancaire - Étape 2 : saisie de la date d’expiration et CVV
@login_required
def carte_bancaire_etape2(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if 'cb_numero' not in request.session:
        return redirect('abonnement:carte_bancaire_etape1')
    if request.method == 'POST':
        date_exp = request.POST.get('date_exp')
        cvv = request.POST.get('cvv')
        if len(date_exp) != 5 or not cvv.isdigit() or len(cvv) != 3:
            messages.error(request, "Date ou CVV invalide.")
            return redirect('abonnement:carte_bancaire_etape2')
        request.session['cb_exp'] = date_exp
        request.session['cb_cvv'] = cvv
        return redirect('abonnement:carte_bancaire_etape3')
    return render(request, 'abonnement/carte_bancaire_etape2.html')

# Carte Bancaire - Étape 3 : saisie du code 3D Secure (simulé)
@login_required
def carte_bancaire_etape3(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if 'cb_numero' not in request.session:
        return redirect('abonnement:carte_bancaire_etape1')
    if request.method == 'POST':
        code = request.POST.get('code_3d')
        if code != '5678':
            messages.error(request, "Code 3D Secure incorrect.")
            return redirect('abonnement:carte_bancaire_etape3')
        request.session['cb_paye'] = True
        return redirect('abonnement:carte_bancaire_confirmation')
    return render(request, 'abonnement/carte_bancaire_etape3.html')

# Carte Bancaire - Étape finale : confirmation et création de l'abonnement
@login_required
def carte_bancaire_confirmation(request):
    # Empêche les administrateurs d'accéder à cette vue
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")

    # Vérifie que le paiement a bien été effectué
    if not request.session.get('cb_paye'):
        return redirect('abonnement:carte_bancaire_etape1')

    # Récupération de la formule "Standard"
    formule = Formule.objects.filter(nom="Standard").first()
    if not formule:
        messages.error(request, "La formule 'Standard' n'existe pas.")
        return redirect('abonnement:choix_mode_paiement')

    # Définition des dates
    date_debut = timezone.now()
    date_expiration = date_debut + relativedelta(months=formule.duree_mois)

    # Création ou mise à jour sécurisée de l’abonnement
    try:
        abonnement = Abonnement.objects.get(user=request.user)
    except Abonnement.DoesNotExist:
        abonnement = Abonnement.objects.create(
            user=request.user,
            formule=formule,
            est_actif=True,
            date_debut=date_debut,
            date_expiration=date_expiration,
            periode_essai=False
        )
    else:
        abonnement.formule = formule
        abonnement.est_actif = True
        abonnement.date_debut = date_debut
        abonnement.date_expiration = date_expiration
        abonnement.periode_essai = False
        abonnement.save()

    # Nettoyage de la session
    for k in ['cb_numero', 'cb_exp', 'cb_cvv', 'cb_paye']:
        request.session.pop(k, None)

    # Redirection en fonction de la situation
    if hasattr(request.user, 'pharmacy') and request.user.pharmacy:
        return redirect('pharmacien:dashboard')
    else:
        return redirect('pharmacien:pharmacy_registration')
    
# Vue pour annuler tout paiement en cours et nettoyer la session
@login_required
def annuler_paiement(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    for k in list(request.session.keys()):
        if k.startswith('om_') or k.startswith('cb_'):
            request.session.pop(k)
    messages.info(request, "Paiement annulé.")
    return redirect('login')

# Vue pour rediriger l'utilisateur à l'enregistrement de la pharmacie
@login_required
def post_abonnement_redirect(request):
    # Empêche a l'admin à acceder à cette route
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    if hasattr(request.user, 'pharmacy'):
        return redirect('pharmacien:dashboard')
    return redirect('pharmacien:pharmacy_registration')
