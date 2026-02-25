

import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as message_constants
from decouple import config

# 🔐 Chargement des variables d’environnement (.env)
load_dotenv()

# 📁 Répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# ⚙️ CONFIGURATION DE BASE
# --------------------------------------------------

# Clé secrète (à garder secrète en production)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'clé_de_secours_pour_le_développement')

# Mode debug (False en production)
DEBUG = True

# Hôtes autorisés à accéder au projet
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# --------------------------------------------------
# 🧩 APPLICATIONS INSTALLÉES
# --------------------------------------------------

INSTALLED_APPS = [
    # Apps Django par défaut
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps tierces
    'django.contrib.humanize',
    'widget_tweaks',
    'django_crontab',

    # Apps du projet
    'interfaceUtilisateur',
    'pharmacien',
    'Produit',
    'gestion_notifications',
    'users',
    'abonnement',
    'administrateur',
]

# --------------------------------------------------
# ⏰ TÂCHES CRON
# --------------------------------------------------

CRONJOBS = [
    ('*/5 * * * *', 'django.core.management.call_command', ['generer_notifications'])
]
CRON_CLASSES = [
    "produit.cron.ExpirationNotificationCronJob",
]

# --------------------------------------------------
# 🔐 MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware personnalisés
    'abonnement.middleware.AbonnementMiddleware',

]

# --------------------------------------------------
# 👥 UTILISATEURS ET AUTHENTIFICATION
# --------------------------------------------------

# Utilisation d’un modèle utilisateur personnalisé
AUTH_USER_MODEL = 'users.User'

# Backends d’authentification
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.auth_backend.BlockedUserBackend',  # Backend personnalisé
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Si besoin
]

# Paramètres Allauth


# Connexion/déconnexion
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'pharmacien:pharmacy_registration'
LOGOUT_REDIRECT_URL = '/home'

# --------------------------------------------------
# 🌍 INTERNATIONALISATION
# --------------------------------------------------

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# 🗃️ TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Tu peux ajouter ici un chemin vers tes templates personnalisés si besoin
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Context processors personnalisés
                # 'gestion_notifications.context_processor.notification_context',
                'gestion_notifications.context_processor.messages_et_notifications',
                'abonnement.context_processors.abonnement_notification',
                'pharmacien.context_processors.pharmacist_notifications',
            ],
        },
    },
]

# --------------------------------------------------
# 🔗 URLS & APPLICATION WSGI
# --------------------------------------------------

ROOT_URLCONF = 'gestionPharmacie.urls'
WSGI_APPLICATION = 'gestionPharmacie.wsgi.application'

# --------------------------------------------------
# 🛢️ BASE DE DONNÉES
# --------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': 'Pharmacie',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# --------------------------------------------------
# 📁 FICHIERS STATIQUES & MÉDIAS
# --------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --------------------------------------------------
# 📬 EMAIL
# --------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
CONTACT_RECEIVER_EMAIL = os.getenv('CONTACT_RECEIVER_EMAIL')

# --------------------------------------------------
# 💬 MESSAGES DJANGO
# --------------------------------------------------

MESSAGE_TAGS = {
    message_constants.INFO: 'info',
    message_constants.DEBUG: 'debug',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'error',
}

# --------------------------------------------------
# 🔐 SÉCURITÉ DES SESSIONS
# --------------------------------------------------

SESSION_COOKIE_AGE = 1209600 if DEBUG else 3600  # 2 semaines en dev, 1h en prod
SESSION_SAVE_EVERY_REQUEST = True


# --------------------------------------------------
# 🔐 VALIDATEURS DE MOT DE PASSE
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# 🔧 DIVERS
# --------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL absolue personnalisée pour les utilisateurs (exemple)
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: '/pharmacien/administration_dashboard/',
}

# OAuth Google (via Allauth)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': '',
        }
    }
}

# --------------------------------------------------
# 🛑 GESTION DES ERREURS
# --------------------------------------------------

# Page 404 personnalisée
handler404 = "interfaceUtilisateur.views.custom_404_view"
