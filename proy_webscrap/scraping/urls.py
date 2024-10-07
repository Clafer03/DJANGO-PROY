from django.urls import path
from . import views

urlpatterns = [
    path('scrap_view/', views.product_list, name='scrap_view'),
]

