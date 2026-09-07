from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from visitas.forms import VisitaForm
from visitas.models import Experiencia, Visita


def home(request):
    if request.method == 'POST':
        form = VisitaForm(request.POST)
        if form.is_valid():
            visita = form.save()
            return redirect('visitas:sucesso', pk=visita.pk)
    else:
        form = VisitaForm()

    experiencias = Experiencia.objects.filter(ativa=True)
    return render(request, 'visitas/home.html', {'form': form, 'experiencias': experiencias})


def sucesso(request, pk):
    visita = get_object_or_404(Visita, pk=pk)
    link_acompanhamento = request.build_absolute_uri(
        reverse('visitas:minha_visita', kwargs={'token': visita.token}),
    )
    return render(request, 'visitas/sucesso.html', {'visita': visita, 'link_acompanhamento': link_acompanhamento})


def minha_visita(request, token):
    visita = get_object_or_404(Visita.objects.select_related('experiencia'), token=token)

    if request.method == 'POST':
        if visita.pode_cancelar_pelo_visitante():
            visita.status = Visita.Status.CANCELADA
            visita.cancelada_por_visitante = True
            visita.save(update_fields=['status', 'cancelada_por_visitante', 'atualizado_em'])
            messages.success(request, 'Visita cancelada.')
        else:
            messages.error(
                request,
                f'Não foi possível cancelar — o prazo é de {Visita.HORAS_LIMITE_CANCELAMENTO}h antes da visita.',
            )
        return redirect('visitas:minha_visita', token=token)

    return render(request, 'visitas/minha_visita.html', {'visita': visita})
