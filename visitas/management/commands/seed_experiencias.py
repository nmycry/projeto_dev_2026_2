from django.core.management.base import BaseCommand

from visitas.models import Experiencia

EXPERIENCIAS = [
    {
        'titulo': 'Visita Clássica',
        'descricao': 'Passeio guiado pelo alambique com explicação do processo de produção da cachaça.',
        'duracao_minutos': 60,
        'preco': '35.00',
        'capacidade_por_horario': 20,
    },
    {
        'titulo': 'Degustação Guiada',
        'descricao': 'Visita ao alambique seguida de degustação comentada de diferentes rótulos.',
        'duracao_minutos': 90,
        'preco': '65.00',
        'capacidade_por_horario': 12,
    },
    {
        'titulo': 'Tour do Alambique com Almoço',
        'descricao': 'Experiência completa: visita, degustação e almoço típico mineiro no local.',
        'duracao_minutos': 180,
        'preco': '150.00',
        'capacidade_por_horario': 8,
    },
]


class Command(BaseCommand):
    help = 'Cria as experiências iniciais do alambique (idempotente).'

    def handle(self, *args, **options):
        for dados in EXPERIENCIAS:
            titulo = dados.pop('titulo')
            _, criada = Experiencia.objects.get_or_create(titulo=titulo, defaults=dados)
            if criada:
                self.stdout.write(self.style.SUCCESS(f'Criada: {titulo}'))
            else:
                self.stdout.write(f'Já existia: {titulo}')
