from django.urls import path
from . import views

urlpatterns = [
    path('', views.shared_expense_list, name='shared_expense_list'),
    path('create/', views.shared_expense_create, name='shared_expense_create'),
    path('<int:pk>/', views.shared_expense_detail, name='shared_expense_detail'),
    path('settle/<int:participant_pk>/', views.settle_payment, name='settle_payment'),
]
