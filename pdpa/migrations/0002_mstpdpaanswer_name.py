# Generated by Django 5.0.7 on 2024-08-27 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdpa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mstpdpaanswer',
            name='name',
            field=models.CharField(default='gg', max_length=255),
            preserve_default=False,
        ),
    ]
