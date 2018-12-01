"""language_app_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from lang_app import views
from django.conf.urls.static import static
from django.conf import settings
from registration.backends.simple.views import RegistrationView
from lang_app.models import UserState
from django.contrib.auth import authenticate, login
from random import shuffle


class MyRegistrationView(RegistrationView):

    def get_success_url(self, user):
        return '/'

    '''
    This function overrides the one in django-redux.
    We need to do this to make sure that there is a
    user profile associated with each user
    '''
    def register(self, form):
        if form.is_valid():
            user = form.save()

            username_field = getattr(user, 'USERNAME_FIELD', 'username')
            user = authenticate(
                username=getattr(user, username_field),
                password=form.cleaned_data['password1']
            )

            login(self.request, user)

            user.save()
            user_state = UserState(user=user)

            # Randomise the order of the policies
            policy_ids = [policy_id for policy_id in user_state.policy_ids]
            shuffle(policy_ids)
            policy_ids = "".join(policy_ids)
            user_state.policy_ids = policy_ids
            user_state.save()
            return user


urlpatterns = [
    path('', views.index, name='index'),
    path('lang-app/', include('lang_app.urls')),
    path('admin/', admin.site.urls),
    path('accounts/register/', MyRegistrationView.as_view(), name='registration_register'),
    path('accounts/', include('registration.backends.simple.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
