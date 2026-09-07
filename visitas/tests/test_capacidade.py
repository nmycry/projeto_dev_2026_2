import datetime

from django.test import TestCase
from django.urls import reverse

from visitas.forms import VisitaForm
from visitas.models import Experiencia, Visita


class CapacidadePorHorarioTests(TestCase):
    def setUp(self):
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=10,
        )
        self.amanha = datetime.date.today() + datetime.timedelta(days=1)
        self.horario = datetime.time(14, 0)

    def _criar_visita(self, num_pessoas, status=Visita.Status.PENDENTE, horario=None):
        return Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=self.amanha,
            horario=horario or self.horario,
            num_pessoas=num_pessoas,
            status=status,
        )

    def _dados_validos(self, **sobrescreve):
        dados = {
            'nome': 'João Souza',
            'email': 'joao@exemplo.com',
            'telefone': '',
            'experiencia': self.experiencia.pk,
            'data': self.amanha.isoformat(),
            'horario': self.horario.strftime('%H:%M'),
            'num_pessoas': 2,
            'observacoes': '',
        }
        dados.update(sobrescreve)
        return dados

    def test_agendamento_dentro_da_capacidade_passa(self):
        self._criar_visita(num_pessoas=8)

        form = VisitaForm(data=self._dados_validos(num_pessoas=2))

        self.assertTrue(form.is_valid(), form.errors)

    def test_agendamento_que_estoura_capacidade_e_recusado_com_vagas_restantes(self):
        self._criar_visita(num_pessoas=9)

        form = VisitaForm(data=self._dados_validos(num_pessoas=2))

        self.assertFalse(form.is_valid())
        self.assertIn('Restam 1 lugares às 14:00', form.non_field_errors()[0])

    def test_visita_cancelada_nao_conta_na_capacidade(self):
        self._criar_visita(num_pessoas=9, status=Visita.Status.CANCELADA)
        self._criar_visita(num_pessoas=9, status=Visita.Status.CONFIRMADA)

        form = VisitaForm(data=self._dados_validos(num_pessoas=1))

        self.assertTrue(form.is_valid(), form.errors)

    def test_editar_visita_sem_mudar_horario_nao_acusa_conflito_falso(self):
        visita = self._criar_visita(num_pessoas=10)

        form = VisitaForm(data=self._dados_validos(num_pessoas=10), instance=visita)

        self.assertTrue(form.is_valid(), form.errors)

    def test_sugestao_de_horario_vizinho_com_vaga(self):
        self._criar_visita(num_pessoas=9)
        self._criar_visita(num_pessoas=2, horario=datetime.time(15, 30))

        form = VisitaForm(data=self._dados_validos(num_pessoas=2))

        self.assertFalse(form.is_valid())
        self.assertIn('15:30', form.non_field_errors()[0])

    def test_cancelar_visita_devolve_a_vaga(self):
        visita_existente = self._criar_visita(num_pessoas=10, status=Visita.Status.CONFIRMADA)

        form_lotado = VisitaForm(data=self._dados_validos(num_pessoas=1))
        self.assertFalse(form_lotado.is_valid())

        visita_existente.status = Visita.Status.CANCELADA
        visita_existente.save(update_fields=['status', 'atualizado_em'])

        form_com_vaga = VisitaForm(data=self._dados_validos(num_pessoas=1))
        self.assertTrue(form_com_vaga.is_valid(), form_com_vaga.errors)
