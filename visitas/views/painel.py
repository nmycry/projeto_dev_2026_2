import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from visitas.forms import ExperienciaForm
from visitas.models import Experiencia, Visita


class PainelBaseView(LoginRequiredMixin):
    """Toda view do painel deve herdar desta classe (nesta ordem, antes da view concreta)."""


class PainelHomeView(PainelBaseView, TemplateView):
    template_name = 'visitas/painel/home.html'


class VisitaListView(PainelBaseView, ListView):
    model = Visita
    template_name = 'visitas/painel/visita_list.html'
    context_object_name = 'visitas'
    paginate_by = 20

    def get_queryset(self):
        queryset = Visita.objects.select_related('experiencia')

        status = self.request.GET.get('status', '').upper()
        if status in Visita.Status.values:
            queryset = queryset.filter(status=status)

        busca = self.request.GET.get('q', '').strip()
        if busca:
            queryset = queryset.filter(Q(nome__icontains=busca) | Q(email__icontains=busca))

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        querystring = self.request.GET.copy()
        querystring.pop('page', None)

        contexto['status_atual'] = self.request.GET.get('status', '').upper()
        contexto['q_atual'] = self.request.GET.get('q', '')
        contexto['status_choices'] = Visita.Status.choices
        contexto['querystring'] = querystring.urlencode()

        page_obj = contexto.get('page_obj')
        tem_resultado_no_filtro = page_obj.paginator.count > 0 if page_obj else bool(contexto['object_list'])
        contexto['existe_visita'] = tem_resultado_no_filtro or Visita.objects.exists()
        return contexto


class VisitaDetailView(PainelBaseView, DetailView):
    model = Visita
    template_name = 'visitas/painel/visita_detail.html'
    queryset = Visita.objects.select_related('experiencia')


MENSAGENS_TRANSICAO = {
    Visita.Status.CONFIRMADA: 'Visita confirmada.',
    Visita.Status.CANCELADA: 'Visita cancelada.',
}


@login_required
@require_POST
def visita_mudar_status(request, pk):
    visita = get_object_or_404(Visita.objects.select_related('experiencia'), pk=pk)
    novo_status = request.POST.get('status', '').upper()

    if novo_status in Visita.Status.values and visita.pode_transicionar_para(novo_status):
        visita.status = novo_status
        visita.save(update_fields=['status', 'atualizado_em'])
        sucesso, texto = True, MENSAGENS_TRANSICAO.get(novo_status, 'Status atualizado.')
    else:
        sucesso = False
        texto = f'Essa visita já está {visita.get_status_display().lower()} — a transição não é permitida.'

    if not request.headers.get('HX-Request'):
        (messages.success if sucesso else messages.error)(request, texto)
        return redirect('visitas:visita_detail', pk=visita.pk)

    resposta = render(request, 'visitas/painel/_linha_visita.html', {'visita': visita})
    evento = 'toast-sucesso' if sucesso else 'toast-erro'
    resposta['HX-Trigger'] = json.dumps({evento: texto})
    return resposta


class ExperienciaListView(PainelBaseView, ListView):
    model = Experiencia
    template_name = 'visitas/painel/experiencia_list.html'
    context_object_name = 'experiencias'
    ordering = ['titulo']


class ExperienciaCreateView(PainelBaseView, CreateView):
    model = Experiencia
    form_class = ExperienciaForm
    template_name = 'visitas/painel/experiencia_form.html'
    success_url = reverse_lazy('visitas:experiencia_list')

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Experiência criada.')
        return resposta


class ExperienciaUpdateView(PainelBaseView, UpdateView):
    model = Experiencia
    form_class = ExperienciaForm
    template_name = 'visitas/painel/experiencia_form.html'
    success_url = reverse_lazy('visitas:experiencia_list')

    def form_valid(self, form):
        desativando = 'ativa' in form.changed_data and not form.cleaned_data['ativa']
        resposta = super().form_valid(form)

        if desativando:
            pendentes_futuras = self.object.visitas.filter(
                status=Visita.Status.PENDENTE,
                data__gte=datetime.date.today(),
            ).count()
            if pendentes_futuras:
                messages.warning(
                    self.request,
                    f'Experiência desativada. Atenção: existem {pendentes_futuras} '
                    'visita(s) pendente(s) futura(s) para essa experiência.',
                )
            else:
                messages.success(self.request, 'Experiência desativada.')
        else:
            messages.success(self.request, 'Experiência salva.')

        return resposta
