from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Amount,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import MyUser


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткого отображения рецепта"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = ['__all__']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class MyUserSerializer(UserSerializer):
    """Сериализатор отображения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MyUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.followings.filter(user=user).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор управления подписками."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(MyUserSerializer.Meta):
        fields = [
            *MyUserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        ]
        read_only_fields = ['__all__']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.followings.filter(user=user).exists()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        return SmallRecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__']


class AmountSerializer(serializers.ModelSerializer):
    """Сериализатор для количества ингридиента в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    author = MyUserSerializer(read_only=True)
    image = serializers.SerializerMethodField(
        'get_image',
        read_only=True,
    )
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ['__all__']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_ingredients(self, obj):
        queryset = obj.amounts.all()
        return AmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopcarts.filter(user=user).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения рецепта."""
    image = Base64ImageField()
    author = MyUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Такой ингридиент уже есть.'}
                )
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if not int(amount) >= 1:
                raise serializers.ValidationError(
                    {'amount': 'Кол-во ингредиента должно быть не менее 1.'}
                )

        if not data['tags']:
            raise serializers.ValidationError(
                {'tags': 'Выберите хотя бы один тэг.'}
            )
        tag_list = []
        for tag in data['tags']:
            if tag in tag_list:
                raise serializers.ValidationError(
                    {'tags': 'Тэги должны быть уникальными.'}
                )
            tag_list.append(tag)

        cook_time = data['cooking_time']
        if not int(cook_time) >= 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть не меньше 1'}
            )
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredient_list = [
            Amount(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ]
        recipe.amounts.bulk_create(ingredient_list)

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class BaseListSerializer(serializers.ModelSerializer):
    """Базовый сериализатор изменения списка."""

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            error_message = self.get_error_message()
            raise serializers.ValidationError(
                {'error': error_message}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SmallRecipeSerializer(instance.recipe, context=context).data

    def get_error_message(self):
        return 'Уже есть'


class FavoriteSerializer(BaseListSerializer):
    """Сериализатор изменения списка избранных рецептов."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def get_error_message(self):
        return 'Этот рецепт уже в избранных'


class ShoppingCartSerializer(BaseListSerializer):
    """Сериализатор изменения списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def get_error_message(self):
        return 'Этот рецепт уже в списке покупок'
