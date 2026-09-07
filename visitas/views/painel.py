from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView

from visitas.models import Visita


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
