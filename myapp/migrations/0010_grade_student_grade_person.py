# Generated by Django 4.1.2 on 2022-10-27 17:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0009_nonmodel"),
    ]

    operations = [
        migrations.CreateModel(
            name="Grade",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="globally unique id (UUID4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "effective_start_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        help_text="date when this instance becomes valid",
                        null=True,
                    ),
                ),
                (
                    "effective_end_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        help_text="date when this instance becomes invalid",
                        null=True,
                    ),
                ),
                (
                    "last_mod_user_name",
                    models.CharField(
                        default=None,
                        help_text="who last modified this instance",
                        max_length=80,
                        null=True,
                    ),
                ),
                (
                    "last_mod_date",
                    models.DateField(auto_now=True, help_text="when they modified it"),
                ),
                ("credits", models.FloatField(help_text="Credits attempted/earned")),
                (
                    "grade_letter",
                    models.CharField(
                        choices=[
                            (None, None),
                            ("A", "A"),
                            ("B", "B"),
                            ("C", "C"),
                            ("D", "D"),
                            ("F", "F"),
                            ("P", "P"),
                        ],
                        default=None,
                        max_length=2,
                    ),
                ),
                (
                    "grade_value",
                    models.FloatField(
                        default=0.0, help_text="grade points (e.g. A is 4.0, F is 0.0)"
                    ),
                ),
                (
                    "course_term",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="grade",
                        to="myapp.courseterm",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="globally unique id (UUID4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "effective_start_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        help_text="date when this instance becomes valid",
                        null=True,
                    ),
                ),
                (
                    "effective_end_date",
                    models.DateField(
                        blank=True,
                        default=None,
                        help_text="date when this instance becomes invalid",
                        null=True,
                    ),
                ),
                (
                    "last_mod_user_name",
                    models.CharField(
                        default=None,
                        help_text="who last modified this instance",
                        max_length=80,
                        null=True,
                    ),
                ),
                (
                    "last_mod_date",
                    models.DateField(auto_now=True, help_text="when they modified it"),
                ),
                (
                    "grades",
                    models.ManyToManyField(related_name="student", to="myapp.grade"),
                ),
                (
                    "person",
                    models.OneToOneField(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student",
                        to="myapp.person",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddField(
            model_name="grade",
            name="person",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="grade",
                to="myapp.student",
            ),
        ),
    ]