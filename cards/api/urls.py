from django.urls import path

from cards.api import views


urlpatterns = [
    path('authorisation/',
         views.AuthorisationView.as_view(),
         name='authorisation'),
]
