# Generated by Django 4.1.7 on 2023-03-03 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('codigo', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('Nombre_Apellido', models.CharField(max_length=50)),
                ('Direccion', models.CharField(max_length=50)),
                ('Ciudad', models.CharField(max_length=15)),
                ('Telefono', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
