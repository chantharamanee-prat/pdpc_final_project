# Generated by Django 5.0.7 on 2024-09-13 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdpa', '0006_alter_mstpdpaanswer_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mstpdpaquestion',
            name='is_request_file',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
