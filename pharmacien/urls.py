from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
app_name = 'pharmacien'

urlpatterns = [
    #url de la page dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    #Les urls de connexion
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    #Les urls de la pharmacie
    path('pharmacy-registration/', views.pharmacy_registration, name='pharmacy_registration'),
    path('ma-pharmacie/', views.my_pharmacy, name='my_pharmacy'),
    
   #les urls du coté profile
   path('mon-profil/', views.profile, name='profile'),
   path('modifier-email/', views.update_email, name='update_email'),
   path('modifier-mot-de-passe/', views.update_password, name='update_password'),

]