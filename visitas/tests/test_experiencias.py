import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class ExperienciaCrudTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=20,
        )

    def _dados_validos(self, **sobrescreve):
        dados = {
            'titulo': 'Visita Clássica',
            'descricao': 'Passeio guiado.',
            'duracao_minutos': 60,
            'preco': '35.00',
            'capacidade_por_horario': 20,
            'ativa': True,
        }
        dados.update(sobrescreve)
        return dados

    def test_lista_exige_login(self):
        resposta = self.client.get(reverse('visitas:experiencia_list'))
        self.assertEqual(resposta.status_code, 302)

    def test_criar_exige_login(self):
        resposta = self.client.get(reverse('visitas:experiencia_create'))
        self.assertEqual(resposta.status_code, 302)

    def test_editar_exige_login(self):
        resposta = self.client.get(reverse('visitas:experiencia_update', args=[self.experiencia.pk]))
        self.assertEqual(resposta.status_code, 302)

    def test_criar_experiencia(self):
        self.client.login(username='responsavel', password='senha-forte-123')

        resposta = self.client.post(
            reverse('visitas:experiencia_create'),
            self._dados_validos(titulo='Tour Completo'),
        )

        self.assertRedirects(resposta, reverse('visitas:experiencia_list'))
        self.assertTrue(Experiencia.objects.filter(titulo='Tour Completo').exists())

    def test_desativar_experiencia_sem_visita_pendente_futura(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        url = reverse('visitas:experiencia_update', args=[self.experiencia.pk])

        resposta = self.client.post(url, self._dados_validos(ativa=False), follow=True)

        self.experiencia.refresh_from_db()
        self.assertFalse(self.experiencia.ativa)
        self.assertContains(resposta, 'Experiência desativada.')

    def test_desativar_experiencia_avisa_quantidade_de_visitas_pendentes_futuras(self):
        Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=datetime.date.today() + datetime.timedelta(days=5),
            horario=datetime.time(14, 0),
            num_pessoas=2,
            status=Visita.Status.PENDENTE,
        )
        self.client.login(username='responsavel', password='senha-forte-123')
        url = reverse('visitas:experiencia_update', args=[self.experiencia.pk])

        resposta = self.client.post(url, self._dados_validos(ativa=False), follow=True)

        self.assertContains(resposta, '1 visita(s) pendente(s) futura(s)')

    def test_experiencia_desativada_some_da_home_publica_mas_visita_antiga_continua(self):
        visita = Visita.objects.create(
            nome='Maria Silva',
            email='maria@exemplo.com',
            experiencia=self.experiencia,
            data=datetime.date.today(),
            horario=datetime.time(14, 0),
            num_pessoas=2,
            status=Visita.Status.CONFIRMADA,
        )
        self.experiencia.ativa = False
        self.experiencia.save(update_fields=['ativa'])

        resposta_home = self.client.get(reverse('visitas:home'))
        self.assertNotContains(resposta_home, 'Visita Clássica')

        self.client.login(username='responsavel', password='senha-forte-123')
        resposta_detalhe = self.client.get(reverse('visitas:visita_detail', args=[visita.pk]))
        self.assertContains(resposta_detalhe, 'Visita Clássica')
