# Generated by Django 5.0.1 on 2024-01-16 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_monitoring'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='alerted',
            field=models.BooleanField(default=False),
        ),
    ]