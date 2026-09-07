import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitas', '0005_visita_token_preencher_existentes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visita',
            name='token',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
