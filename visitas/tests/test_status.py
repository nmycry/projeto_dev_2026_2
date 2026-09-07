import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class VisitaMudarStatusTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=20,
        )

    def _criar_visita(self, status=Visita.Status.PENDENTE):
        return Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=datetime.date.today(),
            horario=datetime.time(14, 0),
            num_pessoas=2,
            status=status,
        )

    def test_confirmar_visita_pendente_via_htmx_devolve_so_o_fragmento(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        visita = self._criar_visita()
        url = reverse('visitas:visita_mudar_status', args=[visita.pk])

        resposta = self.client.post(url, {'status': 'CONFIRMADA'}, HTTP_HX_REQUEST='true')

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn(b'<html', resposta.content)
        self.assertIn('toast-sucesso', resposta.headers['HX-Trigger'])
        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CONFIRMADA)

    def test_cancelar_visita_confirmada_via_htmx(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        visita = self._criar_visita(status=Visita.Status.CONFIRMADA)
        url = reverse('visitas:visita_mudar_status', args=[visita.pk])

        resposta = self.client.post(url, {'status': 'CANCELADA'}, HTTP_HX_REQUEST='true')

        self.assertEqual(resposta.status_code, 200)
        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CANCELADA)

    def test_transicao_invalida_e_recusada_no_backend(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        visita = self._criar_visita(status=Visita.Status.CANCELADA)
        url = reverse('visitas:visita_mudar_status', args=[visita.pk])

        resposta = self.client.post(url, {'status': 'CONFIRMADA'}, HTTP_HX_REQUEST='true')

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('toast-erro', resposta.headers['HX-Trigger'])
        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CANCELADA)

    def test_sem_htmx_redireciona_com_mensagem(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        visita = self._criar_visita()
        url = reverse('visitas:visita_mudar_status', args=[visita.pk])

        resposta = self.client.post(url, {'status': 'CONFIRMADA'})

        self.assertRedirects(resposta, reverse('visitas:visita_detail', args=[visita.pk]))
        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.CONFIRMADA)
