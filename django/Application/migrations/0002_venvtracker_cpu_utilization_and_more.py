# Generated by Django 5.0.2 on 2024-02-11 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='venvtracker',
            name='cpu_utilization',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='venvtracker',
            name='memory_utilization',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='venvtracker',
            name='process_id',
            field=models.IntegerField(null=True),
        ),
    ]
