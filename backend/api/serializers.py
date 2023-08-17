from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import MyUser, Follow
from app.models import Recipe


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткого отображения рецепта"""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = ['__all__']


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
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор управления подписками."""
    recipes = SmallRecipeSerializer(read_only=True, many=True)
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
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
