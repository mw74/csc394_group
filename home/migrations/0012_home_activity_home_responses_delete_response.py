# Generated by Django 4.2 on 2023-05-25 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_remove_home_activity_remove_home_responses_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='home',
            name='activity',
            field=models.CharField(default='N/A', max_length=60000),
        ),
        migrations.AddField(
            model_name='home',
            name='responses',
            field=models.CharField(default='N/A', max_length=50000),
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]
