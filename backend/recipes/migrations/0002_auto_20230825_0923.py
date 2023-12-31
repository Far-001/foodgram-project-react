# Generated by Django 3.2.3 on 2023-08-25 02:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amount',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, help_text='Укажите необходимое количество ингредиентов', validators=[django.core.validators.MinValueValidator(1, message='Количество должно быть не менее 1')], verbose_name='количество'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите единицу измерения', max_length=50, verbose_name='единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, help_text='Введите название ингредиента', max_length=100, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Укажите время в минутах', validators=[django.core.validators.MinValueValidator(1, message='Время должно быть не менее 1 минуты')], verbose_name='время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='static/images/DefaultCardImg.png', help_text='Добавьте изображение', upload_to='recipe_images/%Y/%m/%d', verbose_name='изображение'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(db_index=True, help_text='Введите название рецепта', max_length=256, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='дата публикации'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(help_text='Введите описание рецепта', max_length=1000, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#00ff8f', max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Введенное значение не является цветом в формате HEX!', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='цветовой HEX-код'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Введите уникальную строку', max_length=100, unique=True, verbose_name='слаг'),
        ),
    ]
