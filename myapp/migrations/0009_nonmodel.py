# Generated by Django 4.1.2 on 2022-10-24 17:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0008_auto_20210414_2018"),
    ]

    operations = [
        migrations.CreateModel(
            name="NonModel",
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
                ("field1", models.CharField(max_length=20)),
                ("field2", models.CharField(default="hi", max_length=20)),
                ("field3", models.CharField(default="there", max_length=10)),
            ],
            options={
                "managed": False,
            },
        ),
    ]