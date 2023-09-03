from django.contrib.admin import ModelAdmin, TabularInline, site

from .models import Amount, Favorite, Ingredient, Recipe, ShoppingCart, Tag


class AmountInline(TabularInline):
    """
    Позволяет выводить кол-во ингредиентов в карточке рецепта через модель
    Amount.
    """
    model = Amount
    extra = 1


class RecipeAdmin(ModelAdmin):
    """
    Отображение модели Recipe в админ панели.
    Выводит в карточке рецепта кол-во добавления в избранное и список покупок.
    В список рецептов добавлено поле с тегами.
    """
    list_display = ('name', 'author', 'display_tags')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username', 'author__last_name',
                     'author__first_name', 'tags__name')
    readonly_fields = ('favorite_count', 'shopping_count')
    filter_vertical = ('tags', 'ingredients')
    inlines = (AmountInline,)
    empty_value_display = '-нет-'

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def favorite_count(self, obj):
        return obj.favorites.count()

    def shopping_count(self, obj):
        return obj.shopcarts.count()

    display_tags.short_description = 'Теги'
    favorite_count.short_description = 'В избранном'
    shopping_count.short_description = 'В списке покупок'


class IngredientAdmin(ModelAdmin):
    """Кастомное отображение модели Ingredient."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class AmountAdmin(ModelAdmin):
    """Кастомное отображение модели Amount."""
    list_display = ('recipe', 'ingredient', 'amount')


site.register(Recipe, RecipeAdmin)
site.register(Ingredient, IngredientAdmin)
site.register(Amount, AmountAdmin)
site.register(Tag)
site.register(Favorite)
site.register(ShoppingCart)
