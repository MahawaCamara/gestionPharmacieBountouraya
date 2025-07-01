from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
app_name = 'pharmacien'

urlpatterns = [
    # #url de la page dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Enregistrement et gestion de la pharmacie
    path('register_pharmacy/', views.pharmacy_registration, name='pharmacy_registration'),
    path('my_pharmacy/', views.my_pharmacy, name='my_pharmacy'),

    # Profil utilisateur
    path('profil/', views.profile, name='profile'),
    path('modifier-infos/', views.sensitive_change_form, name='sensitive_change_form'),
    path('verifier-code/', views.verify_sensitive_code, name='verify_sensitive_code'),

]