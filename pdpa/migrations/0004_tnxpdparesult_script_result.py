# Generated by Django 5.0.7 on 2024-08-27 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdpa', '0003_remove_tnxpdparesult_session_tnxpdparesult_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='tnxpdparesult',
            name='script_result',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
