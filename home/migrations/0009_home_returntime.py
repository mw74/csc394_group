# Generated by Django 4.2 on 2023-05-25 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_home_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='home',
            name='returnTime',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
    ]
