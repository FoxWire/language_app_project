from django.urls import path
from lang_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-hint/', views.get_hint, name='get_hint')
]
