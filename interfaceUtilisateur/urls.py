
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='home'),
    path('home/', views.index, name='home'),
    path('details/<int:id>/', views.public_product_details, name='public_product_details'),
    path('search/record_and_notify/', views.record_search_and_notify_pharmacy, name='record_search_and_notify_pharmacy'),
    path('nous-rejoindre/', views.rejoindre, name='rejoindre'),

]
