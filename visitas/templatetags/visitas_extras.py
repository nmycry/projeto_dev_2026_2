from django import template
from django.db.models import Avg, Sum

register = template.Library()


@register.filter
def duracao_media(experiencias):
    media = experiencias.aggregate(media=Avg('duracao_minutos'))['media']
    return round(media) if media is not None else None


@register.filter
def capacidade_total(experiencias):
    return experiencias.aggregate(total=Sum('capacidade_por_horario'))['total']


@register.filter
def intervalo(n):
    return range(n)
