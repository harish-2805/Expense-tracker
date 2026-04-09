from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Friends
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/send/', views.send_friend_request, name='send_friend_request'),
    path('friends/<int:pk>/<str:action>/', views.respond_friend_request, name='respond_friend_request'),
    path('friends/remove/<int:pk>/', views.remove_friend, name='remove_friend'),
]
