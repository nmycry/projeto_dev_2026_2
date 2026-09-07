from django.shortcuts import get_object_or_404, redirect, render

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
    return render(request, 'visitas/sucesso.html', {'visita': visita})
