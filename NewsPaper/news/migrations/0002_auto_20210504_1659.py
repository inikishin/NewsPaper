# Generated by Django 3.2 on 2021-05-04 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]