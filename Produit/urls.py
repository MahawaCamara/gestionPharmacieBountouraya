from django.urls import path
from . import views
from .views import search_products

urlpatterns = [
    path('', views.add_product, name='add_product'),
    path('ajouter/', views.add_product, name='add_product'),
    path('liste/', views.product_list, name='product_list'),
    path('modifier/<int:product_id>/', views.edit_product, name='edit_product'),
    path('supprimer/<int:product_id>/', views.delete_product, name='delete_product'),
    path('details/<int:id>/', views.product_detail, name='product_detail'),
    path('search/', search_products, name='search_products'),
    path('historique-recherches/', views.search_history, name='search_history'),
    
    

]
