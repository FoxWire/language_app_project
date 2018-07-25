from django.urls import path
from lang_app import views

urlpatterns = [
    path('', views.index, name='index')
]
