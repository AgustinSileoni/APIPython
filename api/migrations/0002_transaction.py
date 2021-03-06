# Generated by Django 4.0.1 on 2022-02-10 21:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.FloatField(default=0.0)),
                ('fecha_realizada', models.DateTimeField(auto_now_add=True)),
                ('destino', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='destino', to=settings.AUTH_USER_MODEL)),
                ('origen', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='origen', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
