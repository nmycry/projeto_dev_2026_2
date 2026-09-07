import uuid
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone


class Experiencia(models.Model):
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    duracao_minutos = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    capacidade_por_horario = models.PositiveIntegerField()
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo


class Visita(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    TRANSICOES_PERMITIDAS = {
        Status.PENDENTE: {Status.CONFIRMADA, Status.CANCELADA},
        Status.CONFIRMADA: {Status.CANCELADA},
        Status.CANCELADA: set(),
    }

    HORAS_LIMITE_CANCELAMENTO = 24

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    experiencia = models.ForeignKey(
        Experiencia,
        on_delete=models.PROTECT,
        related_name='visitas',
    )
    data = models.DateField()
    horario = models.TimeField()
    num_pessoas = models.PositiveIntegerField()
    observacoes = models.TextField(blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    compareceu = models.BooleanField(null=True, default=None)
    cancelada_por_visitante = models.BooleanField(default=False)

    class Meta:
        ordering = ['data', 'horario']

    def __str__(self):
        return f'{self.nome} - {self.experiencia} ({self.data} {self.horario})'

    def pode_transicionar_para(self, novo_status):
        return novo_status in self.TRANSICOES_PERMITIDAS.get(self.status, set())

    def pode_cancelar_pelo_visitante(self):
        if not self.pode_transicionar_para(self.Status.CANCELADA):
            return False

        inicio_visita = timezone.make_aware(datetime.combine(self.data, self.horario))
        limite = timezone.now() + timedelta(hours=self.HORAS_LIMITE_CANCELAMENTO)
        return inicio_visita > limite
