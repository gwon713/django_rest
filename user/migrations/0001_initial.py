# Generated by Django 3.2.15 on 2022-10-24 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "email",
                    models.EmailField(
                        max_length=320, unique=True, verbose_name="user_email"
                    ),
                ),
                (
                    "nick_name",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="user_nick_name",
                    ),
                ),
                (
                    "password",
                    models.CharField(max_length=255, verbose_name="user_password"),
                ),
                ("name", models.CharField(max_length=50, verbose_name="user_name")),
                (
                    "phone_number",
                    models.CharField(
                        max_length=13, unique=True, verbose_name="user_phone_number"
                    ),
                ),
                (
                    "last_login_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="user_last_login_at"
                    ),
                ),
            ],
            options={
                "db_table": "user",
            },
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["id"], name="user_id_f1790c_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="user_email_7bbb4c_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["phone_number"], name="user_phone_n_2e859d_idx"),
        ),
    ]
