from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class PainelBaseView(LoginRequiredMixin):
    """Toda view do painel deve herdar desta classe (nesta ordem, antes da view concreta)."""


class PainelHomeView(PainelBaseView, TemplateView):
    template_name = 'visitas/painel/home.html'
