"""
URL configuration for gestionPharmacie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('interfaceUtilisateur.urls')),
    path('interfaceUtilisateur/', include('interfaceUtilisateur.urls')),
    path('account/', include('users.urls')),
    path('pharmacien/', include('pharmacien.urls' , namespace='pharmacien')),
    path('produit/', include('Produit.urls')), 
    path('notifications/', include('gestion_notifications.urls')),
    path('abonnement/', include('abonnement.urls')),
    path('admin/', include('administrateur.urls', namespace='administration')),

]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

