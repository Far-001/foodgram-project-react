from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters

from app.models import Ingredient, Recipe, Tag
from users.models import MyUser


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по их названию."""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value), output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору, тегу, подписке, наличию в списке покупок."""
    author = filters.ModelChoiceFilter(queryset=MyUser.objects.all(),)
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    in_favorited = filters.BooleanFilter(method='filter_in_favorited')
    in_shopping_cart = filters.BooleanFilter(method='filter_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'in_favorited', 'in_shopping_cart')

    def filter_is_favorited(self, queryset, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopcarts__user=self.request.user)
        return queryset
