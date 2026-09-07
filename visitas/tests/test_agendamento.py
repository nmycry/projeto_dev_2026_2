import datetime

from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class AgendamentoPublicoTests(TestCase):
    def setUp(self):
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=20,
        )
        self.amanha = datetime.date.today() + datetime.timedelta(days=1)

    def _dados_validos(self, **sobrescreve):
        dados = {
            'nome': 'Maria Silva',
            'email': 'maria@exemplo.com',
            'telefone': '',
            'experiencia': self.experiencia.pk,
            'data': self.amanha.isoformat(),
            'horario': '14:00',
            'num_pessoas': 2,
            'observacoes': '',
        }
        dados.update(sobrescreve)
        return dados

    def test_post_valido_cria_visita_pendente(self):
        antes = Visita.objects.count()

        resposta = self.client.post(reverse('visitas:home'), self._dados_validos())

        self.assertEqual(Visita.objects.count(), antes + 1)
        visita = Visita.objects.latest('id')
        self.assertEqual(visita.status, Visita.Status.PENDENTE)
        self.assertEqual(visita.nome, 'Maria Silva')
        self.assertEqual(visita.email, 'maria@exemplo.com')
        self.assertEqual(visita.experiencia, self.experiencia)
        self.assertEqual(visita.num_pessoas, 2)
        self.assertRedirects(resposta, reverse('visitas:sucesso', args=[visita.pk]))

    def test_post_invalido_nao_cria_visita(self):
        antes = Visita.objects.count()

        resposta = self.client.post(reverse('visitas:home'), self._dados_validos(num_pessoas=0))

        self.assertEqual(Visita.objects.count(), antes)
        self.assertEqual(resposta.status_code, 200)
        self.assertFormError(resposta.context['form'], 'num_pessoas', 'Informe pelo menos 1 pessoa.')

    def test_experiencia_desativada_e_recusada_no_post(self):
        self.experiencia.ativa = False
        self.experiencia.save(update_fields=['ativa'])
        antes = Visita.objects.count()

        resposta = self.client.post(reverse('visitas:home'), self._dados_validos())

        self.assertEqual(Visita.objects.count(), antes)
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context['form'].errors.get('experiencia'))
