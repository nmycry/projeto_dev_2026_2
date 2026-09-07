import random
from datetime import time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from visitas.models import Experiencia, Visita

NOMES = [
    'Maria Silva', 'João Souza', 'Ana Pereira', 'Carlos Oliveira', 'Fernanda Lima',
    'Pedro Costa', 'Juliana Almeida', 'Rafael Santos', 'Camila Rocha', 'Bruno Ferreira',
    'Larissa Martins', 'Diego Carvalho', 'Patrícia Gomes', 'Rodrigo Barbosa', 'Beatriz Nunes',
    'Thiago Ribeiro', 'Aline Cardoso', 'Marcelo Teixeira', 'Vanessa Correia', 'Gustavo Dias',
]

HORARIOS = [time(9, 0), time(10, 30), time(14, 0), time(15, 30), time(17, 0)]

STATUS_PESOS = [
    (Visita.Status.PENDENTE, 4),
    (Visita.Status.CONFIRMADA, 5),
    (Visita.Status.CANCELADA, 1),
]


class Command(BaseCommand):
    help = 'Popula ~200 visitas variadas para testar paginação e filtro (só em DEBUG).'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Este comando só roda com DEBUG=True (ambiente de desenvolvimento).')

        experiencias = list(Experiencia.objects.all())
        if not experiencias:
            raise CommandError('Nenhuma Experiencia cadastrada. Rode "seed_experiencias" antes.')

        status_valores = [status for status, _ in STATUS_PESOS]
        status_pesos = [peso for _, peso in STATUS_PESOS]

        hoje = timezone.localdate()
        Visita.objects.filter(observacoes='Gerada por seed_visitas.').delete()

        criadas = 0
        for _ in range(200):
            Visita.objects.create(
                nome=random.choice(NOMES),
                email=f'visitante{random.randint(1, 9999)}@exemplo.com',
                telefone='',
                experiencia=random.choice(experiencias),
                data=hoje + timedelta(days=random.randint(-60, 60)),
                horario=random.choice(HORARIOS),
                num_pessoas=random.randint(1, 8),
                observacoes='Gerada por seed_visitas.',
                status=random.choices(status_valores, weights=status_pesos)[0],
            )
            criadas += 1

        self.stdout.write(self.style.SUCCESS(f'{criadas} visitas criadas.'))
