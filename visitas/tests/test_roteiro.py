import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class RoteiroHojeTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')
        self.client.login(username='responsavel', password='senha-forte-123')
        self.experiencia = Experiencia.objects.create(
            titulo='Visita Clássica',
            descricao='Passeio guiado.',
            duracao_minutos=60,
            preco='35.00',
            capacidade_por_horario=20,
        )

    def _criar_visita(self, nome, status, data=None, horario=None, num_pessoas=2):
        return Visita.objects.create(
            nome=nome,
            email=f'{nome.lower().replace(" ", ".")}@exemplo.com',
            experiencia=self.experiencia,
            data=data or datetime.date.today(),
            horario=horario or datetime.time(14, 0),
            num_pessoas=num_pessoas,
            status=status,
        )

    def test_roteiro_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('visitas:roteiro_hoje'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)

    def test_estado_vazio_sem_visita_confirmada_hoje(self):
        resposta = self.client.get(reverse('visitas:roteiro_hoje'))
        self.assertContains(resposta, 'Nenhuma visita confirmada para hoje')

    def test_so_confirmadas_de_hoje_aparecem(self):
        self._criar_visita('Maria Pendente', Visita.Status.PENDENTE)
        self._criar_visita('Joao Cancelado', Visita.Status.CANCELADA)
        self._criar_visita(
            'Ana Amanha', Visita.Status.CONFIRMADA,
            data=datetime.date.today() + datetime.timedelta(days=1),
        )
        self._criar_visita('Carla Hoje', Visita.Status.CONFIRMADA)

        resposta = self.client.get(reverse('visitas:roteiro_hoje'))

        self.assertContains(resposta, 'Carla Hoje')
        self.assertNotContains(resposta, 'Maria Pendente')
        self.assertNotContains(resposta, 'Joao Cancelado')
        self.assertNotContains(resposta, 'Ana Amanha')

    def test_agrupa_por_horario_e_soma_total_geral(self):
        self._criar_visita('Carla', Visita.Status.CONFIRMADA, horario=datetime.time(10, 0), num_pessoas=3)
        self._criar_visita('Bruno', Visita.Status.CONFIRMADA, horario=datetime.time(10, 0), num_pessoas=2)
        self._criar_visita('Diego', Visita.Status.CONFIRMADA, horario=datetime.time(15, 0), num_pessoas=4)

        resposta = self.client.get(reverse('visitas:roteiro_hoje'))

        grupos = resposta.context['grupos']
        self.assertEqual(len(grupos), 2)
        self.assertEqual(grupos[0]['total_pessoas'], 5)
        self.assertEqual(grupos[1]['total_pessoas'], 4)
        self.assertEqual(resposta.context['total_geral'], 9)

    def test_navegacao_por_data_via_querystring(self):
        outro_dia = datetime.date.today() + datetime.timedelta(days=2)
        self._criar_visita('Visitante Futuro', Visita.Status.CONFIRMADA, data=outro_dia)

        resposta = self.client.get(reverse('visitas:roteiro_hoje'), {'data': outro_dia.isoformat()})

        self.assertContains(resposta, 'Visitante Futuro')

    def test_agrupamento_nao_gera_query_por_visita(self):
        for indice in range(6):
            self._criar_visita(f'Visitante {indice}', Visita.Status.CONFIRMADA, horario=datetime.time(9 + indice, 0))

        with self.assertNumQueries(3):
            resposta = self.client.get(reverse('visitas:roteiro_hoje'))
            list(resposta.context['grupos'])


class VisitaMarcarPresencaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')
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
            status=Visita.Status.CONFIRMADA,
        )

    def test_exige_login(self):
        url = reverse('visitas:visita_marcar_presenca', args=[self.visita.pk])

        resposta = self.client.post(url, {'compareceu': 'presente'})

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)
        self.visita.refresh_from_db()
        self.assertIsNone(self.visita.compareceu)

    def test_marcar_presente_via_htmx(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        url = reverse('visitas:visita_marcar_presenca', args=[self.visita.pk])

        resposta = self.client.post(url, {'compareceu': 'presente'}, HTTP_HX_REQUEST='true')

        self.assertEqual(resposta.status_code, 200)
        self.visita.refresh_from_db()
        self.assertTrue(self.visita.compareceu)

    def test_marcar_ausente_via_htmx(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        url = reverse('visitas:visita_marcar_presenca', args=[self.visita.pk])

        resposta = self.client.post(url, {'compareceu': 'ausente'}, HTTP_HX_REQUEST='true')

        self.assertEqual(resposta.status_code, 200)
        self.visita.refresh_from_db()
        self.assertFalse(self.visita.compareceu)

    def test_sem_htmx_redireciona_para_roteiro(self):
        self.client.login(username='responsavel', password='senha-forte-123')
        url = reverse('visitas:visita_marcar_presenca', args=[self.visita.pk])

        resposta = self.client.post(url, {'compareceu': 'presente'})

        self.assertRedirects(resposta, reverse('visitas:roteiro_hoje'))
