from django.urls import path
from lang_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authenticate/', views.authenticate_user, name='authenticate_user'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('get-hint/', views.get_hint, name='get_hint')
]
