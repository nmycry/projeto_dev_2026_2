from django.db.models import Sum

from visitas.models import Visita


def pessoas_reservadas(experiencia, data, horario, excluir_pk=None):
    """Soma num_pessoas das visitas não canceladas naquele (experiencia, data, horario)."""
    queryset = Visita.objects.filter(
        experiencia=experiencia,
        data=data,
        horario=horario,
    ).exclude(status=Visita.Status.CANCELADA)

    if excluir_pk is not None:
        queryset = queryset.exclude(pk=excluir_pk)

    return queryset.aggregate(total=Sum('num_pessoas'))['total'] or 0


def vagas_restantes(experiencia, data, horario, excluir_pk=None):
    ocupadas = pessoas_reservadas(experiencia, data, horario, excluir_pk=excluir_pk)
    return experiencia.capacidade_por_horario - ocupadas


def sugerir_horarios_vizinhos(experiencia, data, horario, num_pessoas, limite=3):
    """Horários de outras visitas (não canceladas) no mesmo dia com vaga para num_pessoas.

    Não existe grade fixa de horário no modelo — só sugere entre horários que já
    têm alguma visita marcada, ordenados pela proximidade em minutos do horário pedido.
    """
    horarios_candidatos = (
        Visita.objects.filter(experiencia=experiencia, data=data)
        .exclude(status=Visita.Status.CANCELADA)
        .exclude(horario=horario)
        .values_list('horario', flat=True)
        .distinct()
    )

    def minutos(h):
        return h.hour * 60 + h.minute

    sugestoes = [
        candidato
        for candidato in horarios_candidatos
        if vagas_restantes(experiencia, data, candidato) >= num_pessoas
    ]
    sugestoes.sort(key=lambda h: abs(minutos(h) - minutos(horario)))
    return sugestoes[:limite]
