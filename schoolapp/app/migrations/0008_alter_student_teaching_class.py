# Generated by Django 4.2.3 on 2025-05-07 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_behaviorhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='teaching_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='app.teachingclass'),
        ),
    ]
