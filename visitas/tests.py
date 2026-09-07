import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from visitas.forms import VisitaForm
from visitas.models import Experiencia, Visita


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

    def test_exige_login(self):
        visita = self._criar_visita()
        url = reverse('visitas:visita_mudar_status', args=[visita.pk])

        resposta = self.client.post(url, {'status': 'CONFIRMADA'})

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('visitas:login'), resposta.url)
        visita.refresh_from_db()
        self.assertEqual(visita.status, Visita.Status.PENDENTE)

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
