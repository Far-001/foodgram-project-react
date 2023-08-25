from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

User = get_user_model()

RECIPE_SHOTNAME = 20
MAX_NAME_LEN = 100


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        'название',
        max_length=MAX_NAME_LEN,
        db_index=True,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=50,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Модель тега.
    Сортировка по имени тега
    """
    name = models.CharField(
        'название',
        max_length=MAX_NAME_LEN,
        db_index=True,
        unique=True
    )
    color = models.CharField(
        'цветовой HEX-код',
        max_length=7,
        unique=True,
        default='#00ff8f',
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(
        'слаг',
        max_length=MAX_NAME_LEN,
        unique=True,
        help_text='Введите уникальную строку'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.
    Поле ingredients связывается с моделью Ingredient,
    через промежуточную модель Amount.
    Поле tags связывается с моделью Tag
    Сортировка по дате публикации(сначала новые).
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Введите автора'
    )
    name = models.CharField(
        'название',
        max_length=256,
        db_index=True,
        help_text='Введите название рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Amount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Укажите теги'
    )
    image = models.ImageField(
        'изображение',
        upload_to='recipe_images/%Y/%m/%d',
        default='static/images/DefaultCardImg.png',
        help_text='Добавьте изображение'
    )
    text = models.TextField(
        'описание',
        max_length=1000,
        help_text='Введите описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        null=False,
        validators=[
            MinValueValidator(
                1,
                message='Время должно быть не менее 1 минуты'
            )
        ],
        help_text='Укажите время в минутах',
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:RECIPE_SHOTNAME]


class Amount(models.Model):
    """
    Промежуточная модель, связывающая Ingredient и Recipe,
    для указания количества ингредиентов в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'количество',
        validators=[
            MinValueValidator(
                1,
                message='Количество должно быть не менее 1'
            )
        ],
        default=1,
        null=False,
        help_text='Укажите необходимое количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: {self.ingredient.name}'
                f'{self.amount}, {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """Избранные рецепты пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'У пользователя {self.user} в избранном {self.recipe}'


class ShoppingCart(models.Model):
    """Рецепты для списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopcarts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopcarts',
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return f'У {self.user} в списке покупок {self.recipe}'
