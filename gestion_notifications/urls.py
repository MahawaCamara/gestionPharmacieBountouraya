# gestion_notifications/urls.py

from django.urls import path
from . import views

# Important : 'notif_views' n'est pas utilisé ici car toutes les vues sont importées via 'from . import views'.
# Vous pouvez supprimer la ligne 'from gestion_notifications import views as notif_views' si elle n'est pas utilisée ailleurs.

app_name = "gestion_notifications"

urlpatterns = [
    # --- URLs pour le Pharmacien ---

    # Gestion des messages du Pharmacien
    # Note : Le nommage des URLs est crucial pour les appels 'reverse' dans les templates.
    # J'ai ajouté 'pharmacien_' pour les rendre uniques et claires.
    path('pharmacien/messages/boite_reception/', views.boite_reception, name='pharmacien_boite_reception'),
    path('pharmacien/messages/detail/<int:message_id>/', views.detail_message, name='pharmacien_detail_message'),
    path('pharmacien/messages/supprimer/<int:id>/', views.supprimer_message, name='pharmacien_supprimer_message'),
    path('pharmacien/messages/marquer_lu/<int:message_id>/', views.marquer_message_lu, name='pharmacien_marquer_message_lu'),
    path('pharmacien/messages/marquer_tous_lus/', views.marquer_tous_messages_lus, name='pharmacien_marquer_tous_messages_lus'),
    path('pharmacien/messages/nombre_non_lus/', views.nombre_messages_non_lus, name='pharmacien_nombre_messages_non_lus'),
    path('pharmacien/messages/recent_unread/', views.get_recent_unread_messages, name='pharmacien_recent_unread_messages'),

    # Gestion des notifications du Pharmacien
    # Les URLs avec des paramètres spécifiques (comme <int:pk>/) doivent venir après les URLs sans paramètres.
    path('pharmacien/notifications/all/', views.toutes_les_notifications, name='pharmacien_toutes_les_notifications'),
    path('pharmacien/notifications/pharmacien/', views.notifications_pharmacien, name='pharmacien_notifications_liste'), # Renommé pour clarté
    path('pharmacien/notifications/mark_all/', views.mark_all_notifications_as_read, name='pharmacien_mark_all_notifications_as_read'),
    path('pharmacien/notifications/get_notifications_ajax/', views.get_notifications, name='pharmacien_get_notifications_ajax'),
    path('pharmacien/notifications/tout_supprimer/', views.tout_supprimer_notifications, name='pharmacien_tout_supprimer_notifications'),
    path('pharmacien/notifications/marquer_toutes_lues/', views.marquer_toutes_comme_lues, name='pharmacien_marquer_toutes_comme_lues'),

    # URLs de notifications avec ID pour le Pharmacien (plus spécifiques)
    path('pharmacien/notifications/detail/<int:pk>/', views.detail_notification, name='pharmacien_detail_notification'),
    path('pharmacien/notifications/mark_as_read/<int:notif_id>/', views.mark_notification_as_read, name='pharmacien_mark_notification_as_read'),
    path('pharmacien/notifications/supprimer/<int:pk>/', views.supprimer_notification, name='pharmacien_supprimer_notification'),
    path('pharmacien/notifications/marquer_lue/<int:pk>/', views.marquer_comme_lue, name='pharmacien_marquer_comme_lue'),


    # --- URLs pour l'Administrateur ---

    # Gestion des messages de l'Admin
    path('admin/messages/envoyer/', views.envoyer_message_admin, name='admin_envoyer_message'), # Message envoyé à l'admin
    path('admin/messages/boite_reception/', views.admin_boite_reception, name='admin_boite_reception'),
    path('admin/messages/detail/<int:message_id>/', views.admin_detail_message, name='admin_detail_message'),

    # Gestion des notifications de l'Admin
    path('admin/notifications/all/', views.admin_toutes_notifications, name='admin_toutes_notifications'),
    path('admin/notifications/mark_all_read/', views.marquer_tout_lu, name='admin_marquer_tout_lu'),
    path('admin/notifications/delete_all/', views.supprimer_toutes_notifications_admin, name='admin_supprimer_toutes_notifications'),

    # URLs de notifications avec ID pour l'Admin (plus spécifiques)
    path('admin/notifications/detail/<int:notif_id>/', views.notification_detail, name='admin_detail_notification'),
    path('admin/notifications/mark_read/<int:notif_id>/', views.marquer_lu, name='admin_marquer_lu'),
    path('admin/notifications/delete/<int:notif_id>/', views.supprimer_notification_admin, name='admin_supprimer_notification'),

    # --- URLs AJAX communes (accessibles par les deux, la logique est dans la vue) ---
    # Ces URLs peuvent être appelées depuis n'importe quel rôle, la vue décide quoi renvoyer.
    path('common/notifications/unread_count/', views.unread_notifications_count, name='common_unread_notifications_count'),
    path('common/notifications/recent_unread/', views.recent_unread_notifications, name='common_recent_unread_notifications'),
    # Note: 'nombre_messages_non_lus' et 'unread_messages_count' pointaient vers la même vue.
    # J'ai gardé le nom le plus descriptif pour l'URL commune des messages non lus.
    path('common/messages/unread_count/', views.nombre_messages_non_lus, name='common_unread_messages_count'),
    # Note: 'recent_unread_messages' était déjà un nom unique et descriptif.
    path('common/messages/recent_unread/', views.get_recent_unread_messages, name='common_recent_unread_messages'),

    # Autres URLs si nécessaire (comme pour les tests de cron job)
    # path('test_cron_expiration/', views.test_cron_expiration, name='test_cron_expiration'),
]