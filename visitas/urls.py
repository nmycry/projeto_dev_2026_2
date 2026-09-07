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
    path('painel/hoje/', painel.roteiro_hoje, name='roteiro_hoje'),
    path('painel/hoje/<int:pk>/presenca/', painel.visita_marcar_presenca, name='visita_marcar_presenca'),
    path('painel/visitas/', painel.VisitaListView.as_view(), name='visita_list'),
    path('painel/visitas/<int:pk>/', painel.VisitaDetailView.as_view(), name='visita_detail'),
    path('painel/visitas/<int:pk>/status/', painel.visita_mudar_status, name='visita_mudar_status'),
    path('painel/experiencias/', painel.ExperienciaListView.as_view(), name='experiencia_list'),
    path('painel/experiencias/nova/', painel.ExperienciaCreateView.as_view(), name='experiencia_create'),
    path('painel/experiencias/<int:pk>/editar/', painel.ExperienciaUpdateView.as_view(), name='experiencia_update'),
]
