from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('add/', views.budget_add, name='budget_add'),
    path('<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('<int:pk>/delete/', views.budget_delete, name='budget_delete'),
]
