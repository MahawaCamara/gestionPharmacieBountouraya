from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.custom_login_view, name="login"),
    path("logout/", views.custom_logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # Mot de passe oublié / réinitialisation
    path("mot-de-passe-oublie/", auth_views.PasswordResetView.as_view(
    template_name="user/password_reset.html",
    email_template_name="user/password_reset_email.html",
    subject_template_name="user/password_reset_subject.txt",
    extra_email_context={
        'domain': 'localhost:8000',
        'site_name': 'Plateforme PharmaConnect',
        'protocol': 'http',  # ou 'https' en production
    }
), name="password_reset"),
    path("mot-de-passe-envoye/", auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="user/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/complete/", auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_complete.html"), name="password_reset_complete"),

    # Changer mot de passe connecté
    path("changer-mot-de-passe/", auth_views.PasswordChangeView.as_view(template_name="user/password_change.html"), name="password_change"),
    path("changer-mot-de-passe-ok/", auth_views.PasswordChangeDoneView.as_view(template_name="user/password_change_done.html"), name="password_change_done"),
]
