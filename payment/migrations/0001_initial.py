# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
from decimal import Decimal
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(default=b'none', max_length=32)),
                ('account_id', models.CharField(max_length=128, null=True)),
                ('card_last4', models.CharField(max_length=4, null=True)),
                ('card_type', models.CharField(max_length=32, null=True)),
                ('card_exp_month', models.IntegerField(null=True)),
                ('card_exp_year', models.IntegerField(null=True)),
                ('card_fingerprint', models.CharField(max_length=32, null=True)),
                ('card_country', models.CharField(max_length=2, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_deactivated', models.DateTimeField(null=True)),
                ('status', models.CharField(default=b'ACTIVE', max_length=11, choices=[(b'ACTIVE', b'ACTIVE'), (b'DEACTIVATED', b'DEACTIVATED'), (b'EXPIRED', b'EXPIRED'), (b'EXPIRING', b'EXPIRING'), (b'ERROR', b'ERROR')])),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('pledged', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='credit', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CreditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=16)),
                ('sent', models.IntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('api', models.CharField(max_length=64)),
                ('correlation_id', models.CharField(max_length=512, null=True)),
                ('timestamp', models.CharField(max_length=128, null=True)),
                ('info', models.CharField(max_length=1024, null=True)),
                ('status', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Receiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=64)),
                ('amount', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('currency', models.CharField(max_length=10)),
                ('status', models.CharField(max_length=64)),
                ('local_status', models.CharField(max_length=64, null=True)),
                ('reason', models.CharField(max_length=64)),
                ('primary', models.BooleanField(default=True)),
                ('txn_id', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Sent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=32, null=True)),
                ('amount', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=0)),
                ('host', models.CharField(default=b'none', max_length=32)),
                ('execution', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'None', max_length=32)),
                ('local_status', models.CharField(default=b'NONE', max_length=32, null=True)),
                ('amount', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('max_amount', models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2)),
                ('currency', models.CharField(default=b'USD', max_length=10, null=True)),
                ('secret', models.CharField(max_length=64, null=True)),
                ('pay_key', models.CharField(max_length=128, null=True)),
                ('preapproval_key', models.CharField(max_length=128, null=True)),
                ('receipt', models.CharField(max_length=256, null=True)),
                ('approved', models.NullBooleanField()),
                ('error', models.CharField(max_length=256, null=True)),
                ('reason', models.CharField(max_length=64, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_payment', models.DateTimeField(null=True)),
                ('date_executed', models.DateTimeField(null=True)),
                ('date_authorized', models.DateTimeField(null=True)),
                ('date_expired', models.DateTimeField(null=True)),
                ('extra', jsonfield.fields.JSONField(default={}, null=True)),
                ('anonymous', models.BooleanField(default=False)),
                ('campaign', models.ForeignKey(on_delete=models.CASCADE, to='core.Campaign', null=True)),
                ('offer', models.ForeignKey(on_delete=models.CASCADE, to='core.Offer', null=True)),
                ('premium', models.ForeignKey(on_delete=models.CASCADE, to='core.Premium', null=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='receiver',
            name='transaction',
            field=models.ForeignKey(on_delete=models.CASCADE, to='payment.Transaction'),
        ),
        migrations.AddField(
            model_name='paymentresponse',
            name='transaction',
            field=models.ForeignKey(on_delete=models.CASCADE, to='payment.Transaction'),
        ),
    ]
