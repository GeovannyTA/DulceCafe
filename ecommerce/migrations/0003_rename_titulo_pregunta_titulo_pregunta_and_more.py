# Generated by Django 4.2.6 on 2023-10-22 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_rename_preguntas_pregunta_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pregunta',
            old_name='titulo',
            new_name='titulo_pregunta',
        ),
        migrations.RenameField(
            model_name='respuesta',
            old_name='respuesta',
            new_name='respuesta_pregunta',
        ),
    ]
