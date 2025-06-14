# Generated by Django 4.2.19 on 2025-05-25 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0018_alter_teacher_phone"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimeSlot",
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
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("slot_name", models.CharField(max_length=50)),
                ("is_break", models.BooleanField(default=False)),
                ("order", models.IntegerField()),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="TimeConfiguration",
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
                ("name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slots", models.ManyToManyField(to="mainapp.timeslot")),
            ],
            options={
                "verbose_name": "Time Configuration",
                "verbose_name_plural": "Time Configurations",
            },
        ),
    ]
