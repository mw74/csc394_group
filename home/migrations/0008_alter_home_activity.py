# Generated by Django 4.2 on 2023-05-24 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_alter_home_activity_alter_home_responses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='home',
            name='activity',
            field=models.CharField(default='N/A', max_length=60000),
        ),
    ]
