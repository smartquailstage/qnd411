# Generated by Django 5.0 on 2024-09-17 03:53

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('stock', models.IntegerField(blank=True, null=True)),
                ('precio_unitario', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('address', models.CharField(max_length=250, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('descuentos', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('devoluciones', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('iva_porcentaje', models.DecimalField(decimal_places=2, default=Decimal('15.00'), max_digits=5)),
            ],
            options={
                'ordering': ('-fecha',),
            },
        ),
        migrations.CreateModel(
            name='VentaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='venta_items', to='businessmodel.productos')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='businessmodel.venta')),
            ],
        ),
    ]
