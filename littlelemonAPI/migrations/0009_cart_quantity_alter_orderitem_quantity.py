# Generated by Django 4.1.3 on 2024-03-17 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('littlelemonAPI', '0008_alter_menuitem_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='quantity',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.SmallIntegerField(default=1),
        ),
    ]
