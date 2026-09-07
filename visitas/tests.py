from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PainelProtegidoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')

    def test_painel_redireciona_anonimo_para_login(self):
        resposta = self.client.get(reverse('visitas:painel_home'))
        self.assertRedirects(resposta, f"{reverse('visitas:login')}?next={reverse('visitas:painel_home')}")

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
