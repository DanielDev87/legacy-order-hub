from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_users(apps, schema_editor):
    UserModel = apps.get_model("users", "UserModel")
    if UserModel.objects.exists():
        return
    UserModel.objects.create(
        username="admin", password=make_password("admin123"), role="admin"
    )
    UserModel.objects.create(
        username="juan", password=make_password("123456"), role="client"
    )


def unseed_users(apps, schema_editor):
    UserModel = apps.get_model("users", "UserModel")
    UserModel.objects.filter(username__in=["admin", "juan"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_users, unseed_users),
    ]
