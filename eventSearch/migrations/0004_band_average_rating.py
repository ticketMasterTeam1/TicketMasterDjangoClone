# Generated by Django 4.2.7 on 2023-12-09 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventSearch', '0003_reviews_author_reviews_created_on_reviews_edited_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='average_rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3),
        ),
    ]
