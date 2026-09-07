import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from visitas.models import Experiencia, Visita


class MinhaVisitaTests(TestCase):
    def setUp(self):
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=10,
        )

    def _criar_visita(self, status=Visita.Status.CONFIRMADA, daqui_a_horas=48):
        momento = timezone.localtime() + datetime.timedelta(hours=daqui_a_horas)
        return Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=momento.date(),
            horario=momento.time().replace(microsecond=0),
            num_pessoas=2,
            status=status,
        )

    def test_link_funciona_sem_login_e_mostra_dados_da_visita(self):
        visita = self._criar_visita()

        resposta = self.client.get(reverse('visitas:minha_visita', args=[visita.token]))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Maria Silva')
        self.assertContains(resposta, 'Visita Clássica')

    def test_token_invalido_da_404_sem_vazar_se_existe(self):
        resposta = self.client.get(reverse('visitas:minha_visita', args=['00000000-0000-0000-0000-000000000000']))
        self.assertEqual(resposta.status_code, 404)

    def test_token_de_outra_visita_nao_da_acesso_a_esta(self):
        visita_a = self._criar_visita()
        visita_b = self._criar_visita()

        resposta = self.client.get(reverse('visitas:minha_visita', args=[visita_b.token]))

        self.assertContains(resposta, visita_b.nome)
        self.assertNotEqual(visita_a.token, visita_b.token)

    def test_cancelar_dentro_do_prazo_devolve_a_vaga(self):
        visita = self._criar_visita(daqui_a_horas=48)
        url = reverse('visitas:minha_visita', args=[visita.token])

        resposta = self.client.post(url, follow=True)

        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CANCELADA)
        self.assertTrue(visita.cancelada_por_visitante)
        self.assertContains(resposta, 'Visita cancelada.')

    def test_cancelar_fora_do_prazo_e_recusado_no_backend(self):
        visita = self._criar_visita(daqui_a_horas=2)
        url = reverse('visitas:minha_visita', args=[visita.token])

        resposta = self.client.post(url, follow=True)

        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CONFIRMADA)
        self.assertFalse(visita.cancelada_por_visitante)
        self.assertContains(resposta, 'Não foi possível cancelar')

    def test_visita_ja_cancelada_nao_aceita_novo_cancelamento(self):
        visita = self._criar_visita(status=Visita.Status.CANCELADA)
        url = reverse('visitas:minha_visita', args=[visita.token])

        resposta = self.client.get(url)
        self.assertNotContains(resposta, 'Cancelar visita')

        self.client.post(url, follow=True)
        visita.refresh_from_db()
        self.assertFalse(visita.cancelada_por_visitante)
