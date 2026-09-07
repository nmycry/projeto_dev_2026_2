from django.contrib import admin

from .models import Experiencia, Visita


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'preco', 'duracao_minutos', 'capacidade_por_horario', 'ativa')


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'experiencia', 'data', 'horario', 'status')
