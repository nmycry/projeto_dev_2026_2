from django.urls import path

from visitas.views import publico

app_name = 'visitas'

urlpatterns = [
    path('', publico.home, name='home'),
]
