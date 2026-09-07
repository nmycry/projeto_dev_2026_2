import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class PainelProtegidoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')

    def test_painel_redireciona_anonimo_para_login(self):
        resposta = self.client.get(reverse('visitas:painel_home'))
        self.assertRedirects(resposta, f"{reverse('visitas:login')}?next={reverse('visitas:painel_home')}")

    def test_painel_com_sessao_retorna_200(self):
        self.client.login(username='responsavel', password='senha-forte-123')

        resposta = self.client.get(reverse('visitas:painel_home'))

        self.assertEqual(resposta.status_code, 200)

    def test_login_volta_para_pagina_pedida(self):
        url_painel = reverse('visitas:painel_home')
        resposta = self.client.post(
            f"{reverse('visitas:login')}?next={url_painel}",
            {'username': 'responsavel', 'password': 'senha-forte-123'},
        )
        self.assertRedirects(resposta, url_painel)

    def test_logout_encerra_sessao_e_painel_volta_a_barrar(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        self.client.post(reverse('visitas:logout'))
        resposta = self.client.get(reverse('visitas:painel_home'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)


class VisitaMudarStatusAcessoTests(TestCase):
    def setUp(self):
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=20,
        )
        self.visita = Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=datetime.date.today(),
            horario=datetime.time(14, 0),
            num_pessoas=2,
            status=Visita.Status.PENDENTE,
        )

    def test_post_anonimo_no_endpoint_de_status_nao_altera_nada(self):
        url = reverse('visitas:visita_mudar_status', args=[self.visita.pk])

        resposta = self.client.post(url, {'status': 'CONFIRMADA'})

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)
        self.visita.refresh_from_db()
        self.assertEqual(self.visita.status, Visita.Status.PENDENTE)
