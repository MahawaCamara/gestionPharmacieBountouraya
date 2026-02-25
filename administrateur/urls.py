# administration/urls.py
from django.urls import path
from . import views
app_name = "administration"

urlpatterns = [
    path("", views.dashboard, name="dashboard_admin"),
    path("dashboard/", views.dashboard, name="dashboard_admin"),
    # Les urls de la pharmacie
    path("pharmaciens/", views.manage_pharmacies, name="manage_pharmacies"),
    path('pharmacies/approve/<int:id>/', views.approve_pharmacy, name='approve_pharmacy'),
    path("pharmacie/<int:id>/supprimer/", views.delete_pharmacy, name="delete_pharmacy"),
    path('blocked-users/export-excel/', views.export_pharmacies_excel, name='export_pharmacies_excel'),
    # Les urls du produit
    path("produits/", views.manage_products, name="manage_products"),
    path('produits/<int:id>/supprimer/', views.delete_product, name='delete_product'),
    path('produits/export-excel/', views.export_products_excel, name='export_products_excel'),
    # Gestion des Formes Pharmaceutiques
    path("formes/", views.manage_forms, name="manage_forms"),  # Liste des formes
    path("formes/supprimer/<int:id>/", views.delete_form, name="delete_form"),  # Supprimer une forme
    # Les urls de l'abonnement
    path("abonnements/", views.manage_subscriptions, name="manage_subscriptions"),
    path("admin/abonnements/toggle/<int:id>/", views.toggle_abonnement, name="toggle_abonnement"),
    path("admin/abonnements/export-excel/", views.export_abonnements_excel, name="export_abonnements_excel"),
    # Les urls des produits expirés
    path("produits-expirés/", views.expired_products, name="expired_products"),
    path('export-expired-products-excel/', views.export_expired_products_excel, name='export_expired_products_excel'),
    # Les urls des utilisateurs bloqués
    path('utilisateurs/', views.all_users, name='all_users'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),  # logique pour bloquer un user
    path('blocked-users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked-users/export-excel/', views.export_blocked_users_excel, name='export_blocked_users_excel'),
    path("statistiques/", views.statistics, name="statistics"),
    
    path('profil/', views.admin_profile, name='admin_profile'),

]
