# Generated by Django 4.1 on 2022-08-24 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("naac", "0007_ssr_geo_tag_lat_convert_ssr_geo_tag_latitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="iiqa",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]