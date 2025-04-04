# Generated by Django 5.1.3 on 2024-11-27 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0005_student_branch"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="teacher_code",
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
