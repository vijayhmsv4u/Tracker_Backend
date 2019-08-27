# Generated by Django 2.2.2 on 2019-08-21 10:20

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackerapp', '0002_auto_20190821_0623'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='team_members',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(max_length=255), default=[], size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='projectusers',
            name='role',
            field=models.CharField(choices=[('BACK-END DEVELOPER', 'DEVELOPERS'), ('FRONT-END DEVELOPER', 'DEVELOPERS'), ('TEAM_LEAD', 'TEAM_LEAD'), ('PROJECT_MANAGER', 'PROJECT_MANAGER'), ('CEO', 'CEO'), ('CTO', 'CTO'), ('DEVOPS', 'DEVOPS'), ('DATA_OPERATORS', 'DATA_OPERATORS'), ('DATA_SCIENTIST', 'DATA_SCIENTIST'), ('MANUAL TESTER', 'TESTING'), ('AUTOMATION TESTER', 'TESTING')], max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='designation',
            field=models.CharField(choices=[('BACK-END DEVELOPER', 'DEVELOPERS'), ('FRONT-END DEVELOPER', 'DEVELOPERS'), ('TEAM_LEAD', 'TEAM_LEAD'), ('PROJECT_MANAGER', 'PROJECT_MANAGER'), ('CEO', 'CEO'), ('CTO', 'CTO'), ('DEVOPS', 'DEVOPS'), ('DATA_OPERATORS', 'DATA_OPERATORS'), ('DATA_SCIENTIST', 'DATA_SCIENTIST'), ('MANUAL TESTER', 'TESTING'), ('AUTOMATION TESTER', 'TESTING')], max_length=255),
        ),
    ]