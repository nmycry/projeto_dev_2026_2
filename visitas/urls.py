from django.contrib.auth import views as auth_views
from django.urls import path

from visitas.views import painel, publico

app_name = 'visitas'

urlpatterns = [
    path('', publico.home, name='home'),
    path('agendamento/<int:pk>/sucesso/', publico.sucesso, name='sucesso'),
    path('login/', auth_views.LoginView.as_view(template_name='visitas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('painel/', painel.PainelHomeView.as_view(), name='painel_home'),
    path('painel/visitas/', painel.VisitaListView.as_view(), name='visita_list'),
    path('painel/visitas/<int:pk>/', painel.VisitaDetailView.as_view(), name='visita_detail'),
]
