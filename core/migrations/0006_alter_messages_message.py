# Generated by Django 4.1.2 on 2022-12-13 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='message',
            field=models.CharField(max_length=1000),
        ),
    ]