# Generated by Django 5.0.2 on 2024-03-01 11:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GoDutchApp", "0004_alter_t_expense_detail_payer"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="t_burden_user",
            name="delete_flg",
        ),
        migrations.AlterField(
            model_name="t_burden_user",
            name="burden_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]