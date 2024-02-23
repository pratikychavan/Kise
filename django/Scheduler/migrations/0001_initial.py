# Generated by Django 5.0.2 on 2024-02-23 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Queues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('queue_name', models.CharField(default='', max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SomeTaskReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default='', max_length=50, null=True)),
                ('operation', models.CharField(default='', max_length=50, null=True)),
                ('params', models.JSONField(default=dict, null=True)),
                ('results', models.JSONField(default=dict, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VenvTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task_id', models.CharField(default='', max_length=50, null=True)),
                ('status', models.CharField(default='', max_length=50, null=True)),
                ('process_id', models.IntegerField(null=True)),
                ('cpu_utilization', models.FloatField(null=True)),
                ('memory_utilization', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
