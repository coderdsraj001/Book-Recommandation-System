# Generated by Django 5.1.4 on 2024-12-28 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0002_alter_customuser_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('authors', models.CharField(max_length=255)),
                ('genre', models.CharField(max_length=100)),
                ('publication_date', models.DateField()),
                ('description', models.TextField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
