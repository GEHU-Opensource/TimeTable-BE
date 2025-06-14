# Generated by Django 4.2.19 on 2025-06-14 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0018_alter_teacher_phone"),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chromosome", models.CharField(max_length=20)),
                ("day", models.CharField(max_length=20)),
                ("teacher_id", models.CharField(max_length=100)),
                ("subject_id", models.CharField(max_length=100)),
                ("classroom_id", models.CharField(max_length=20)),
                ("time_slot", models.CharField(max_length=20)),
            ],
            options={
                "db_table": "schedule",
            },
        ),
    ]
