# Generated by Django 5.0.1 on 2024-01-12 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_user_role_routerlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='router',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
