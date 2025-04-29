
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='home'),
    path('home/', views.index, name='home'),
    # path('recherche/ajax/', views.product_search, name='product_search'),
    # path('historique/', views.history_search, name='history_search'),
]
