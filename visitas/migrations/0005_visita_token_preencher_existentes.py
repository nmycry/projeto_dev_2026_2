import uuid

from django.db import migrations


def preencher_tokens(apps, schema_editor):
    Visita = apps.get_model('visitas', 'Visita')
    for visita in Visita.objects.filter(token__isnull=True):
        visita.token = uuid.uuid4()
        visita.save(update_fields=['token'])


class Migration(migrations.Migration):

    dependencies = [
        ('visitas', '0004_visita_token'),
    ]

    operations = [
        migrations.RunPython(preencher_tokens, migrations.RunPython.noop),
    ]
