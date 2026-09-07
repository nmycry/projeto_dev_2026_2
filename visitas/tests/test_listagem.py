import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.models import Experiencia, Visita


class VisitaListViewTests(TestCase):
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

    def _criar_visita(self, nome, email, status, dias=0):
        return Visita.objects.create(
            nome=nome,
            email=email,
            experiencia=self.experiencia,
            data=datetime.date.today() + datetime.timedelta(days=dias),
            horario=datetime.time(14, 0),
            num_pessoas=2,
            status=status,
        )

    def test_lista_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('visitas:visita_list'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)

    def test_estado_vazio_sem_nenhuma_visita_cadastrada(self):
        resposta = self.client.get(reverse('visitas:visita_list'))
        self.assertContains(resposta, 'Nenhuma visita agendada ainda')

    def test_filtro_por_status(self):
        self._criar_visita('Maria Silva', 'maria@exemplo.com', Visita.Status.PENDENTE)
        self._criar_visita('João Souza', 'joao@exemplo.com', Visita.Status.CONFIRMADA)

        resposta = self.client.get(reverse('visitas:visita_list'), {'status': 'confirmada'})

        self.assertContains(resposta, 'João Souza')
        self.assertNotContains(resposta, 'Maria Silva')

    def test_estado_vazio_para_filtro_sem_resultado(self):
        self._criar_visita('Maria Silva', 'maria@exemplo.com', Visita.Status.PENDENTE)

        resposta = self.client.get(reverse('visitas:visita_list'), {'status': 'cancelada'})

        self.assertContains(resposta, 'Nenhuma visita encontrada para esse filtro')

    def test_busca_por_nome_ou_email(self):
        self._criar_visita('Maria Silva', 'maria@exemplo.com', Visita.Status.PENDENTE)
        self._criar_visita('João Souza', 'joao@exemplo.com', Visita.Status.PENDENTE)

        resposta = self.client.get(reverse('visitas:visita_list'), {'q': 'joao@exemplo.com'})

        self.assertContains(resposta, 'João Souza')
        self.assertNotContains(resposta, 'Maria Silva')

    def test_filtro_e_busca_combinam_e_sobrevivem_a_paginacao(self):
        for indice in range(25):
            self._criar_visita(f'Confirmada {indice}', f'confirmada{indice}@exemplo.com', Visita.Status.CONFIRMADA)
        self._criar_visita('Pendente Único', 'pendente@exemplo.com', Visita.Status.PENDENTE)

        resposta = self.client.get(
            reverse('visitas:visita_list'), {'status': 'confirmada', 'q': 'confirmada', 'page': 2}
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.context['visitas']), 5)
        self.assertContains(resposta, 'status=confirmada')
        self.assertContains(resposta, 'q=confirmada')

    def test_lista_nao_gera_query_por_linha_para_experiencia(self):
        for indice in range(10):
            self._criar_visita(f'Visitante {indice}', f'visitante{indice}@exemplo.com', Visita.Status.PENDENTE)

        with self.assertNumQueries(4):
            resposta = self.client.get(reverse('visitas:visita_list'))
            list(resposta.context['visitas'])


class VisitaDetailViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='responsavel', password='senha-forte-123')
        self.client.login(username='responsavel', password='senha-forte-123')
        self.experiencia = Experiencia.objects.create(
            titulo='Degustação Guiada',
            descricao='Visita com degustação.',
            duracao_minutos=90,
            preco='65.00',
            capacidade_por_horario=12,
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

    def test_detalhe_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('visitas:visita_detail', args=[self.visita.pk]))
        self.assertEqual(resposta.status_code, 302)

    def test_detalhe_mostra_dados_da_visita_e_da_experiencia(self):
        resposta = self.client.get(reverse('visitas:visita_detail', args=[self.visita.pk]))
        self.assertContains(resposta, 'Maria Silva')
        self.assertContains(resposta, 'Degustação Guiada')
        self.assertContains(resposta, '65,00')
