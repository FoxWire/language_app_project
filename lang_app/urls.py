from django.urls import path
from lang_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.user_logout, name='user_logout'),
]
