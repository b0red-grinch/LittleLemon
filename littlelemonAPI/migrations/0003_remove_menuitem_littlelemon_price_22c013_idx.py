# Generated by Django 5.0.2 on 2024-02-09 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('littlelemonAPI', '0002_menuitem_delete_book_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='menuitem',
            name='littlelemon_price_22c013_idx',
        ),
    ]
