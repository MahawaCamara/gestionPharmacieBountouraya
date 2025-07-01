from django.urls import path
from . import views

app_name = 'abonnement'

urlpatterns = [
    path('', views.page_abonnement, name='page_abonnement'),
    path('essai-gratuit/', views.essai_gratuit, name='essai_gratuit'),
    path('choix-mode/', views.choix_mode_paiement, name='choix_mode_paiement'),

    # Orange Money étapes
    path('orange-money/etape-1/', views.orange_money_etape1, name='orange_money_etape1'),
    path('orange-money/etape-2/', views.orange_money_etape2, name='orange_money_etape2'),
    path('orange-money/etape-3/', views.orange_money_etape3, name='orange_money_etape3'),
    path('orange-money/confirmation/', views.orange_money_confirmation, name='orange_money_confirmation'),

    # Carte bancaire étapes
    path('carte-bancaire/etape-1/', views.carte_bancaire_etape1, name='carte_bancaire_etape1'),
    path('carte-bancaire/etape-2/', views.carte_bancaire_etape2, name='carte_bancaire_etape2'),
    path('carte-bancaire/etape-3/', views.carte_bancaire_etape3, name='carte_bancaire_etape3'),
    path('carte-bancaire/confirmation/', views.carte_bancaire_confirmation, name='carte_bancaire_confirmation'),
    path('abonnement/post-confirmation/', views.post_abonnement_redirect, name='post_abonnement_redirect'),
    path('annuler/', views.annuler_paiement, name='annuler_paiement'),
]
