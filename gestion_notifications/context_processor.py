# from pharmacien.models import Pharmacy
# from .models import Notification,Message

# def messages_et_notifications(request):
#     context = {
#         'messages_non_lus': [],
#         'messages_non_lus_count': 0,
#         'notifications_recentes': [],
#         'notifications_non_lues_count': 0,
#     }

#     if request.user.is_authenticated:
#         if request.user.is_staff:
#             msgs = Message.objects.filter(destinataire=request.user, est_lu=False)
#             context['messages_non_lus'] = msgs[:5]
#             context['messages_non_lus_count'] = msgs.count()
#         else:
#             try:
#                 pharmacie = request.user.pharmacy
#                 msgs = Message.objects.filter(destinataire=request.user, destinataire_pharmacy=pharmacie, est_lu=False)
#                 context['messages_non_lus'] = msgs[:5]
#                 context['messages_non_lus_count'] = msgs.count()
#             except Pharmacy.DoesNotExist:
#                 pass

#         notifs = Notification.objects.filter(user=request.user, lu=False)
#         context['notifications_recentes'] = notifs[:5]
#         context['notifications_non_lues_count'] = notifs.count()

#     return context

# def messages_non_lus_count(request):
#     if request.user.is_authenticated:
#         try:
#             pharmacie = request.user.pharmacy
#             return {
#                 'messages_non_lus': Message.objects.filter(destinataire_pharmacy=pharmacie, est_lu=False)
#             }
#         except:
#             pass
#     return {'messages_non_lus': []}

# def notification_context(request):
#     if request.user.is_authenticated:
#         notifications_non_lues = Notification.objects.filter(user=request.user, lu=False)[:5]
#         total_non_lues = notifications_non_lues.count()
#         return {
#             'notifications_recentes': notifications_non_lues,
#             'notifications_non_lues_count': total_non_lues
#         }
#     return {}

from pharmacien.models import Pharmacy
from .models import Notification, Message

def messages_et_notifications(request):
    context = {
        'my_app_messages_list': [], # Anciennement 'messages_non_lus'
        'my_app_messages_count': 0, # Anciennement 'messages_non_lus_count'
        'my_app_notifications_list': [], # Anciennement 'notifications_recentes'
        'my_app_notifications_count': 0, # Anciennement 'notifications_non_lues_count'
    }

    if request.user.is_authenticated:
        # --- Logique pour les messages (provenant des clients) ---
        if request.user.is_staff or request.user.is_superuser:
            msgs = Message.objects.filter(destinataire=request.user, est_lu=False)
            context['my_app_messages_list'] = msgs.order_by('-date_envoye')[:5]
            context['my_app_messages_count'] = msgs.count()
        else:
            try:
                pharmacy = Pharmacy.objects.get(user=request.user)
                # Remarque : j'ai laissé la condition 'destinataire=request.user' ici si vous voulez que
                # le pharmacien puisse aussi recevoir des messages qui lui sont directement adressés en tant qu'utilisateur,
                # en plus de ceux adressés à sa pharmacie. Si un message est soit à l'utilisateur, soit à la pharmacie,
                # vous devrez ajuster ce filtre. Souvent, pour un pharmacien, c'est UNIQUEMENT destinataire_pharmacy.
                # Si c'est le cas, changez la ligne ci-dessous en :
                # msgs = Message.objects.filter(destinataire_pharmacy=pharmacy, est_lu=False)
                # ou combinez avec un Q object si les deux cas sont possibles mais exclusifs.
                msgs = Message.objects.filter(
                    destinataire_pharmacy=pharmacy, est_lu=False
                ).order_by('-date_envoye')
                context['my_app_messages_list'] = msgs[:5]
                context['my_app_messages_count'] = msgs.count()
            except Pharmacy.DoesNotExist:
                pass
            except Exception as e:
                # Loguez l'erreur pour le débogage
                print(f"Erreur dans messages_et_notifications pour pharmacien: {e}")
                pass

        # --- Logique pour les notifications internes ---
        notifs = Notification.objects.filter(user=request.user, lu=False)
        context['my_app_notifications_list'] = notifs.order_by('-created_at')[:5] # Assurez-vous d'avoir un champ 'created_at' ou similaire
        context['my_app_notifications_count'] = notifs.count()

    return context

# --- Ce context processor est très probablement le coupable principal s'il est actif ---
# Renommez la clé qu'il retourne. Idéalement, supprimez ce context processor
# et intégrez sa logique dans messages_et_notifications si c'est possible.
def messages_non_lus_count(request):
    if request.user.is_authenticated:
        try:
            pharmacie = request.user.pharmacy
            return {
                # RENOMMEZ CETTE CLÉ AVEC UN PRÉFIXE UNIQUE !
                'my_app_pharmacy_unread_messages_qs': Message.objects.filter(destinataire_pharmacy=pharmacie, est_lu=False)
            }
        except Pharmacy.DoesNotExist:
            pass
        except Exception as e:
            print(f"Erreur dans messages_non_lus_count context processor: {e}")
            pass
    return {'my_app_pharmacy_unread_messages_qs': []}


# --- Ce context processor est également redondant, mais si vous le gardez, modifiez-le ---
def notification_context(request):
    if request.user.is_authenticated:
        try:
            notifications_non_lues = Notification.objects.filter(user=request.user, lu=False).order_by('-created_at')[:5]
            total_non_lues = notifications_non_lues.count()
            return {
                # RENOMMEZ CES CLÉS AVEC UN PRÉFIXE UNIQUE !
                'my_app_global_notifications_recent': notifications_non_lues,
                'my_app_global_notifications_count': total_non_lues
            }
        except Exception as e:
            print(f"Erreur dans notification_context context processor: {e}")
            pass
    return {'my_app_global_notifications_recent': [], 'my_app_global_notifications_count': 0}