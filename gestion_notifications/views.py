from urllib import request
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages as dj_messages
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from gestion_notifications.management.commands.generer_notifications_expiration import verifier_produits_expire
from .forms import MessageForm, ReponseMessageForm
from pharmacien.models import Pharmacy
from .models import Notification, Message
from Produit.models import Product
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q # Import pour des requêtes OR

User = get_user_model()

def admin_required(view_func):
    """
    Décorateur personnalisé pour vérifier si l'utilisateur est un superuser (administrateur).
    """
    return user_passes_test(lambda u: u.is_superuser)(view_func)

# --- Vues de Messages et Notifications pour le Pharmacien ---

@login_required
def boite_reception(request):
    """
    Affiche la boîte de réception des messages pour un utilisateur (pharmacien ou admin).
    Le pharmacien voit les messages destinés à sa pharmacie.
    L'admin voit les messages où il est le destinataire de type User.
    """
    messages_recus = []
    user_role_display = ""

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # L'administrateur voit les messages où il est le destinataire de type User
            messages_recus = Message.objects.filter(destinataire=request.user).order_by('-date_envoye')
            user_role_display = "Administrateur"
        else:
            try:
                # Le pharmacien voit les messages destinés à sa pharmacie
                pharmacy = Pharmacy.objects.get(user=request.user)
                messages_recus = Message.objects.filter(destinataire_pharmacy=pharmacy).order_by('-date_envoye')
                user_role_display = f"Pharmacie: {pharmacy.pharmacy_name}"
            except Pharmacy.DoesNotExist:
                dj_messages.error(request, "Aucune pharmacie associée à votre compte. Veuillez contacter l'administrateur.")
                return redirect('pharmacien:dashboard')
            except Exception as e:
                dj_messages.error(request, f"Une erreur inattendue est survenue lors de la récupération des messages : {e}")
                return redirect('pharmacien:dashboard')
    else:
        return redirect('account_login')

    context = {
        'messages_recus': messages_recus,
        'user_role_display': user_role_display,
    }
    return render(request, 'pharmacien/messages/boite_reception.html', context)


@login_required
def detail_message(request, message_id):
    """
    Affiche les détails d'un message spécifique.
    Marque le message comme lu après consultation.
    Permet au pharmacien de répondre par email à l'expéditeur du message.
    """
    message = None
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            # Récupère le message si l'utilisateur est l'admin destinataire
            message = get_object_or_404(Message, id=message_id, destinataire=request.user)
        else:
            try:
                # Récupère le message si l'utilisateur est un pharmacien de la pharmacie destinataire
                pharmacy = Pharmacy.objects.get(user=request.user)
                message = get_object_or_404(Message, id=message_id, destinataire_pharmacy=pharmacy)
            except Pharmacy.DoesNotExist:
                raise Http404("Pharmacie non trouvée ou message non destiné à votre pharmacie.")
    
    if not message:
        raise Http404("Message introuvable ou accès non autorisé.")

    # Marquer le message comme lu si ce n'est pas déjà fait
    if not message.est_lu:
        message.est_lu = True
        message.save()

    initial_data = {
        'message_id': message.id, 
        'sujet': f"RE: {message.sujet}", 
    }
    form = ReponseMessageForm(initial=initial_data)

    if request.method == 'POST':
        form = ReponseMessageForm(request.POST)
        if form.is_valid():
            sujet_reponse = form.cleaned_data['sujet']
            contenu_reponse = form.cleaned_data['corps']
            
            if message.expediteur_email:
                try:
                    send_mail(
                        subject=sujet_reponse,
                        message=contenu_reponse,
                        from_email=request.user.email,
                        recipient_list=[message.expediteur_email],
                        fail_silently=False,
                    )
                    dj_messages.success(request, "Votre réponse a été envoyée par email au client.")
                except Exception as e:
                    dj_messages.error(request, f"Erreur lors de l'envoi de l'email: {e}. Veuillez vérifier votre configuration email.")
            else:
                dj_messages.warning(request, "Impossible de répondre par email : l'expéditeur n'a pas fourni d'adresse email.")
            
            return redirect('gestion_notifications:pharmacien_detail_message', message_id=message.id)
        else:
            dj_messages.error(request, "Veuillez corriger les erreurs ci-dessous dans le formulaire de réponse.")

    context = {
        'message': message,
        'form': form,
    }
    return render(request, 'pharmacien/messages/detail_message.html', context)

@login_required
def supprimer_message(request, id):
    """
    Permet à un pharmacien de supprimer un message qui lui est destiné.
    Accès interdit pour l'administrateur via cette vue.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit. Cette fonction est pour les pharmaciens.")
    
    try:
        pharmacie = Pharmacy.objects.get(user=request.user)
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à ce compte.")
        return redirect('gestion_notifications:pharmacien_boite_reception')

    message = get_object_or_404(Message, id=id, destinataire_pharmacy=pharmacie)
    message.delete()
    dj_messages.success(request, "Message supprimé avec succès.")
    return redirect('gestion_notifications:pharmacien_boite_reception')


@login_required
@require_POST
def marquer_message_lu(request, message_id):
    """
    Marque un message spécifique comme lu via une requête AJAX.
    Gère les messages pour les administrateurs et les pharmaciens.
    """
    user = request.user
    
    try:
        if user.is_staff or user.is_superuser:
            # L'admin marque son message comme lu
            message = Message.objects.get(id=message_id, destinataire=user)
            message.est_lu = True
            message.save()
            return JsonResponse({'status': 'success', 'message': 'Message administrateur marqué comme lu.'})
        else:
            # Le pharmacien marque son message comme lu
            pharmacie = Pharmacy.objects.get(user=user)
            message = Message.objects.get(id=message_id, destinataire_pharmacy=pharmacie)
            message.est_lu = True
            message.save()
            return JsonResponse({'status': 'success', 'message': 'Message pharmacien marqué comme lu.'})
            
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message introuvable ou non autorisé.'}, status=404)
    except Pharmacy.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pharmacie associée introuvable.'}, status=404)
    except Exception as e:
        print(f"Erreur lors du marquage d'un message comme lu : {e}")
        return JsonResponse({'status': 'error', 'message': f'Erreur lors de l’opération : {e}'}, status=400)


@login_required
@require_POST
def marquer_tous_messages_lus(request):
    """
    Marque tous les messages non lus de l'utilisateur (admin ou pharmacien) comme lus.
    """
    user = request.user
    
    try:
        if user.is_staff or user.is_superuser:
            # L'admin marque tous ses messages comme lus
            Message.objects.filter(destinataire=user, est_lu=False).update(est_lu=True)
            return JsonResponse({'status': 'success', 'message': 'Tous les messages administrateur ont été marqués comme lus.'})
        else:
            # Le pharmacien marque tous ses messages comme lus
            pharmacie = Pharmacy.objects.get(user=user)
            Message.objects.filter(destinataire_pharmacy=pharmacie, est_lu=False).update(est_lu=True)
            return JsonResponse({'status': 'success', 'message': 'Tous les messages pharmacien ont été marqués comme lus.'})
            
    except Pharmacy.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pharmacie associée introuvable.'}, status=404)
    except Exception as e:
        print(f"Erreur lors du marquage de tous les messages comme lus : {e}")
        return JsonResponse({'status': 'error', 'message': f'Erreur lors de l’opération : {e}'}, status=400)


@login_required
def nombre_messages_non_lus(request):
    """
    Retourne le nombre de messages non lus pour l'utilisateur actuel (admin ou pharmacien).
    Utilisé pour l'affichage de badges de notification.
    """
    user = request.user
    count = 0

    try:
        if user.is_staff or user.is_superuser:
            # Admin: messages destinés à l'admin et non lus
            count = Message.objects.filter(destinataire=user, est_lu=False).count()
        elif hasattr(user, 'pharmacy') and user.pharmacy: 
            # Pharmacien: messages destinés à sa pharmacie et non lus
            count = Message.objects.filter(destinataire_pharmacy=user.pharmacy, est_lu=False).count()
        
        return JsonResponse({'unread_count': count}) 
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de messages non lus: {e}")
        return JsonResponse({'unread_count': 0, 'error': f'Erreur interne: {e}'}, status=500)


@login_required
def get_recent_unread_messages(request):
    """
    Récupère les 5 messages non lus les plus récents pour l'utilisateur actuel (admin ou pharmacien).
    Utilisé pour afficher un aperçu des messages dans une interface utilisateur.
    """
    user = request.user
    messages_data = []
    
    try:
        if user.is_staff or user.is_superuser:
            # Admin: 5 messages les plus récents non lus destinés à l'admin
            messages = Message.objects.filter(
                destinataire=user,
                est_lu=False
            ).order_by('-date_envoye')[:5]
        elif hasattr(user, 'pharmacy') and user.pharmacy:
            # Pharmacien: 5 messages les plus récents non lus destinés à sa pharmacie
            messages = Message.objects.filter(
                destinataire_pharmacy=user.pharmacy,
                est_lu=False
            ).order_by('-date_envoye')[:5]
        else:
            messages = Message.objects.none()

        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'expediteur_nom': msg.expediteur_nom,
                'sujet': msg.sujet,
                'date_envoye': msg.date_envoye.isoformat(),
                'corps': msg.corps,
            })
        
        return JsonResponse({'messages': messages_data})
    except Exception as e:
        print(f"Erreur lors de la récupération des messages récents non lus: {e}")
        return JsonResponse({'messages': [], 'error': f'Erreur interne: {e}'}, status=500)


@login_required
def unread_notifications_count(request):
    """
    Retourne le nombre de notifications non lues pour l'utilisateur actuel (admin ou pharmacien).
    """
    user = request.user
    count = 0
    try:
        if user.is_staff or user.is_superuser:
            # Notifications de l'administrateur
            count = Notification.objects.filter(user=user, lu=False).count()
        elif hasattr(user, 'pharmacy') and user.pharmacy:
            # Notifications du pharmacien
            count = Notification.objects.filter(pharmacy=user.pharmacy, lu=False).count()
        return JsonResponse({'unread_count': count})
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de notifications non lues: {e}")
        return JsonResponse({'unread_count': 0, 'error': f'Erreur interne: {e}'}, status=500)

@login_required
def recent_unread_notifications(request):
    """
    Récupère les 5 notifications non lues les plus récentes pour l'utilisateur actuel (admin ou pharmacien).
    """
    user = request.user
    notifications_data = []
    try:
        if user.is_staff or user.is_superuser:
            # Notifications de l'administrateur
            recent_notifications = Notification.objects.filter(
                user=user,
                lu=False
            ).order_by('-date_creation')[:5]
        elif hasattr(user, 'pharmacy') and user.pharmacy:
            # Notifications du pharmacien
            recent_notifications = Notification.objects.filter(
                pharmacy=user.pharmacy,
                lu=False
            ).order_by('-date_creation')[:5]
        else:
            recent_notifications = Notification.objects.none()

        for notif in recent_notifications:
            notifications_data.append({
                'id': notif.id,
                'titre': getattr(notif, 'titre', 'Sans Titre'),
                'message': notif.message,
                'date_creation': notif.date_creation.isoformat(),
                'icon_class': notif.get_icon(),
                'url': reverse('gestion_notifications:detail_notification', args=[notif.id]) # Assurez-vous que cette URL existe dans votre urls.py
            })
        return JsonResponse({'notifications': notifications_data})
    except Exception as e:
        print(f"Erreur lors de la récupération des notifications récentes : {e}")
        return JsonResponse({'notifications': [], 'error': f'Erreur interne: {e}'}, status=500)

@login_required
def toutes_les_notifications(request):
    """
    [PHARMACIEN] Affiche toutes les notifications d'une pharmacie spécifique.
    Accès interdit pour les administrateurs.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit. Cette page est réservée aux pharmaciens.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notifications = Notification.objects.filter(pharmacy=pharmacy).order_by('-date_creation')
    except Pharmacy.DoesNotExist:
        notifications = Notification.objects.none()
        dj_messages.warning(request, "Aucune pharmacie associée à votre compte pour afficher les notifications.")

    return render(request, 'notification/toutes_les_notifications.html', {'notifications': notifications})


@login_required
def mark_notification_as_read(request, notif_id):
    """
    [PHARMACIEN] Marque une notification spécifique comme lue.
    Accès interdit pour les administrateurs.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notif = get_object_or_404(Notification, id=notif_id, pharmacy=pharmacy)
        notif.lu = True
        notif.save()
        dj_messages.success(request, "Notification marquée comme lue.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à votre compte.")
    except Notification.DoesNotExist:
        dj_messages.error(request, "Notification introuvable ou non autorisée.")
    return redirect('gestion_notifications:pharmacien_toutes_les_notifications')


@login_required
def mark_all_notifications_as_read(request):
    """
    [PHARMACIEN] Marque toutes les notifications non lues d'une pharmacie comme lues.
    Accès interdit pour les administrateurs.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        Notification.objects.filter(pharmacy=pharmacy, lu=False).update(lu=True)
        dj_messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à votre compte.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('gestion_notifications:pharmacien_toutes_les_notifications')


@login_required
def get_notifications(request):
    """
    [PHARMACIEN] Récupère les notifications récentes pour une pharmacie (AJAX).
    Accès interdit pour les administrateurs.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    notifications_recentes = Notification.objects.none()
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notifications_recentes = Notification.objects.filter(
            pharmacy=pharmacy, lu=False
        ).order_by('-date_creation')[:5]
    except Pharmacy.DoesNotExist:
        pass

    html = render_to_string('notification/list_notif.html', {
        'notifications_recentes': notifications_recentes
    }, request=request)
    return JsonResponse({'html': html})


def notifier_recherche_produit(user, produit_nom):
    """
    [PHARMACIEN] Crée une notification pour le pharmacien si un produit est recherché publiquement.
    Évite les doublons de notifications trop fréquents pour la même recherche.
    """
    maintenant = timezone.now()
    delai = timedelta(minutes=10)

    derniere_notif = Notification.objects.filter(
        user=user,
        type='produit_recherche',
        message__icontains=produit_nom,
        date_creation__gte=maintenant - delai
    ).first()

    if not derniere_notif:
        pharmacy = Pharmacy.objects.filter(user=user).first()
        if pharmacy:
            Notification.objects.create(
                user=user,
                type='produit_recherche',
                titre=f"Recherche produit '{produit_nom}'",
                message=f"Recherche publique pour '{produit_nom}' concernant votre produit {produit_nom}",
                pharmacy=pharmacy
            )

def generer_notifications_expiration():
    """
    [CRON JOB/TACHE DE FOND] Génère des notifications pour les produits dont la date d'expiration approche.
    """
    aujourd_hui = timezone.now().date()
    seuil = aujourd_hui + timedelta(days=30)

    produits_a_expirer = Product.objects.filter(date_expiration__lte=seuil)

    for produit in produits_a_expirer:
        if produit.pharmacy and produit.pharmacy.user:
            user = produit.pharmacy.user
            Notification.objects.get_or_create(
                user=user,
                pharmacy=produit.pharmacy,
                type='expiration_produit',
                titre=f"Produit bientôt expiré : {produit.nom}",
                message=f"Le produit {produit.nom} expire le {produit.date_expiration}",
            )


@login_required
def notifications_pharmacien(request):
    """
    [PHARMACIEN] Affiche la liste des notifications du pharmacien.
    Redirection vers une page spécifique pour les administrateurs si l'accès est tenté.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notifications = Notification.objects.filter(pharmacy=pharmacy).order_by('-date_creation')
    except Pharmacy.DoesNotExist:
        notifications = Notification.objects.none()
        dj_messages.warning(request, "Aucune pharmacie associée pour afficher les notifications.")

    return render(request, 'notification/pharmacien_notifications.html', {
        'notifications': notifications
    })


@login_required
def marquer_toutes_pharmacien_lues(request):
    """
    [PHARMACIEN] Marque toutes les notifications non lues du pharmacien comme lues.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        Notification.objects.filter(pharmacy=pharmacy, lu=False).update(lu=True)
        dj_messages.success(request, "Toutes vos notifications ont été marquées comme lues.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Impossible de marquer les notifications comme lues : aucune pharmacie associée.")
    
    return redirect('gestion_notifications:pharmacien_notifications')


@login_required
def detail_notification(request, pk):
    """
    [PHARMACIEN] Affiche les détails d'une notification spécifique et la marque comme lue.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notif = get_object_or_404(Notification, pk=pk, pharmacy=pharmacy)
        notif.lu = True
        notif.save()
        dj_messages.success(request, "Notification détaillée et marquée comme lue.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à votre compte.")
    except Notification.DoesNotExist:
        dj_messages.error(request, "Notification introuvable ou non autorisée.")
    
    return redirect('gestion_notifications:pharmacien_toutes_les_notifications')

@login_required
def notification_list(request):
    """
    [PHARMACIEN] Variante de `toutes_les_notifications`, affiche la liste des notifications.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notifications = Notification.objects.filter(pharmacy=pharmacy).order_by('-date_creation')
    except Pharmacy.DoesNotExist:
        notifications = Notification.objects.none()
        dj_messages.warning(request, "Aucune pharmacie associée pour afficher les notifications.")
        
    return render(request, 'gestion_notifications/pharmacien_notifications.html', {'notifications': notifications})

@login_required
def supprimer_notification(request, pk):
    """
    [PHARMACIEN] Supprime une notification spécifique.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notif = get_object_or_404(Notification, id=pk, pharmacy=pharmacy)
        notif.delete()
        dj_messages.success(request, "Notification supprimée avec succès.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à votre compte.")
    except Notification.DoesNotExist:
        dj_messages.error(request, "Notification introuvable ou non autorisée.")
        
    return redirect('gestion_notifications:pharmacien_notifications')

@login_required
def tout_supprimer_notifications(request):
    """
    [PHARMACIEN] Supprime toutes les notifications d'une pharmacie.
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        Notification.objects.filter(pharmacy=pharmacy).delete()
        dj_messages.success(request, "Toutes vos notifications ont été supprimées.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Impossible de supprimer les notifications : aucune pharmacie associée.")
        
    return redirect('gestion_notifications:pharmacien_toutes_les_notifications')

@login_required
def marquer_comme_lue(request, pk):
    """
    [PHARMACIEN] Marque une notification individuelle comme lue (alias de `mark_notification_as_read`).
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        notif = get_object_or_404(Notification, id=pk, pharmacy=pharmacy)
        notif.lu = True
        notif.save()
        dj_messages.success(request, "Notification marquée comme lue.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Aucune pharmacie associée à votre compte.")
    except Notification.DoesNotExist:
        dj_messages.error(request, "Notification introuvable ou non autorisée.")
        
    return redirect('gestion_notifications:pharmacien_toutes_les_notifications')

@login_required
def marquer_toutes_comme_lues(request):
    """
    [PHARMACIEN] Marque toutes les notifications non lues comme lues (alias de `mark_all_notifications_as_read`).
    """
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Accès interdit.")
    
    try:
        pharmacy = Pharmacy.objects.get(user=request.user)
        Notification.objects.filter(pharmacy=pharmacy, lu=False).update(lu=True)
        dj_messages.success(request, "Toutes vos notifications ont été marquées comme lues.")
    except Pharmacy.DoesNotExist:
        dj_messages.error(request, "Impossible de marquer les notifications comme lues : aucune pharmacie associée.")
        
    return redirect('gestion_notifications:pharmacien_notifications')

# --- Vues Spécifiques à l'Administrateur ---

@login_required
def envoyer_message_admin(request):
    """
    [ADMIN] Permet à un utilisateur (généralement un pharmacien) d'envoyer un message à l'administrateur.
    """
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            # Trouve le premier superuser pour le définir comme destinataire
            admin_user = User.objects.filter(is_staff=True, is_superuser=True).first()
            if not admin_user:
                dj_messages.error(request, "Aucun administrateur trouvé pour recevoir le message.")
                return redirect('accueil')
            
            msg.destinataire = admin_user 
            msg.destinataire_pharmacy = None # Un message envoyé à un user admin n'est pas lié à une pharmacy en tant que destinataire
            msg.est_lu = False
            msg.save()
            dj_messages.success(request, "Votre message a bien été envoyé à l'administrateur.")
            return redirect('accueil')
    else:
        form = MessageForm()
    return render(request, 'gestion_notifications/envoyer_message.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_boite_reception(request):
    """
    [ADMIN] Affiche la boîte de réception des messages pour l'administrateur connecté.
    """
    messages_recu = Message.objects.filter(destinataire=request.user).order_by('-date_envoye')
    return render(request, 'administration/boite_reception.html', {'messages_recu': messages_recu})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_detail_message(request, message_id):
    """
    [ADMIN] Affiche les détails d'un message reçu par l'administrateur et permet d'y répondre par email.
    La réponse est également enregistrée comme un message interne si l'expéditeur est un utilisateur enregistré.
    """
    message = get_object_or_404(Message, id=message_id, destinataire=request.user)

    if not message.est_lu:
        message.est_lu = True
        message.save()

    if request.method == 'POST':
        form = ReponseMessageForm(request.POST)
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            corps = form.cleaned_data['corps']

            corps_complet = (
                f"Bonjour {message.expediteur_nom},\n\n"
                f"{corps}\n\n"
                f"---\n"
                f"Réponse de l'administrateur : {request.user.email}\n"
                f"Merci de nous avoir contacté."
            )

            try:
                send_mail(
                    sujet,
                    corps_complet,
                    settings.DEFAULT_FROM_EMAIL,
                    [message.expediteur_email],
                    fail_silently=False,
                )
                dj_messages.success(request, f"Réponse envoyée par email à : {message.expediteur_email}")
            except Exception as e:
                print(f"Erreur d'envoi d'email: {e}")
                dj_messages.error(request, "Erreur lors de l'envoi de l'email. Veuillez réessayer.")
            
            # Créer une réponse dans le système de messages interne si l'expéditeur existe comme User ou Pharmacy
            dest_user = User.objects.filter(email=message.expediteur_email).first()
            dest_pharmacy = Pharmacy.objects.filter(user__email=message.expediteur_email).first()

            if dest_user or dest_pharmacy:
                Message.objects.create(
                    expediteur_nom=request.user.get_full_name() or request.user.email,
                    expediteur_email=request.user.email,
                    sujet=sujet,
                    corps=corps,
                    destinataire=dest_user if dest_user else None,
                    destinataire_pharmacy=dest_pharmacy if dest_pharmacy else None,
                    est_lu=False
                )
                dj_messages.success(request, "Réponse enregistrée dans la boîte de réception interne.")
            else:
                dj_messages.warning(request, "L'expéditeur du message original n'est pas un utilisateur ou une pharmacie enregistrée, la réponse interne ne sera pas enregistrée.")

            return redirect('gestion_notifications:admin_boite_reception')
    else:
        form = ReponseMessageForm(initial={'sujet': f"Re: {message.sujet}"})

    return render(request, 'administration/detail_message.html', {
        'message': message,
        'form': form,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def notification_detail(request, notif_id):
    """
    [ADMIN] Affiche les détails d'une notification spécifique à l'administrateur et la marque comme lue.
    Si la notification est liée à un produit, elle affiche également les détails du produit.
    """
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.lu = True
    notif.save()

    if notif.type == 'expiration_produit' and hasattr(notif, 'content_object') and notif.content_object:
        produit = notif.content_object
        if isinstance(produit, Product):
            return render(request, 'administration/notification_produit_detail.html', {'produit': produit, 'notif': notif})

    return render(request, 'administration/notification_produit_detail.html', {'notif': notif})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_toutes_notifications(request):
    """
    [ADMIN] Affiche toutes les notifications de l'administrateur.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-date_creation')
    return render(request, 'administration/toutes_les_notifications.html', {'notifications': notifications})

@login_required
@admin_required
def marquer_lu(request, notif_id):
    """
    [ADMIN] Marque une notification spécifique de l'administrateur comme lue.
    """
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.lu = True
    notif.save()
    dj_messages.success(request, "Notification marquée comme lue.")
    return redirect('gestion_notifications:admin_toutes_notifications')

@login_required
@admin_required
def marquer_tout_lu(request):
    """
    [ADMIN] Marque toutes les notifications non lues de l'administrateur comme lues.
    """
    Notification.objects.filter(user=request.user, lu=False).update(lu=True)
    dj_messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect('gestion_notifications:admin_toutes_notifications')

@login_required
@admin_required
def supprimer_notification_admin(request, notif_id):
    """
    [ADMIN] Supprime une notification spécifique de l'administrateur.
    """
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.delete()
    dj_messages.success(request, "Notification supprimée avec succès.")
    return redirect('gestion_notifications:admin_toutes_notifications')

@login_required
@admin_required
def supprimer_toutes_notifications_admin(request):
    """
    [ADMIN] Supprime toutes les notifications de l'administrateur.
    """
    Notification.objects.filter(user=request.user).delete()
    dj_messages.success(request, "Toutes les notifications ont été supprimées.")
    return redirect('gestion_notifications:admin_toutes_notifications')