from datetime import datetime

from django.db.models import F, Sum
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.models import MyUser, Follow
from app.models import Ingredient, Amount, Recipe, Tag

from .filters import IngredientFilter, RecipeFilter
from .paginations import RestrictPagination
from .permissions import AuthorStaffOrReadOnly
from .serializers import (
    MyUserSerializer,
    FollowSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeListSerializer,
    RecipeCreateSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)


class MyUserViewSet(UserViewSet):
    """Операции с пользователями."""
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [AllowAny]
    add_serializer = FollowSerializer

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Выдача подписок авторизванным пользователям"""
        user = self.request.user
        authors = MyUser.objects.filter(followings__user=user)
        pages = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписка на автора(отписка) для авторизованных пользователей."""
        user = self.request.user
        author = get_object_or_404(MyUser, id=id)
        subscription = Follow.objects.filter(user=user, author=author)
        subs_message = 'Нельзя подписаться. Уже подписаны!'
        unsubs_message = 'Нельзя отписаться. Вы не подписаны!'

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': subs_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(author, context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': unsubs_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """Получение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Получение ингердиентов. Поиск по названию."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """
    Операции с рецептами.
    Фильтрация по автору, тегу, подписке и наличию в списке покупок.
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = RestrictPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        queryset = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        err_del_message = 'Нельзя удалить рецепт, который не добавлен.'

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not queryset.exists():
                return Response(
                    {'error': err_del_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.action_post_delete(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.action_post_delete(pk, ShoppingCartSerializer)

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated],
            pagination_class=None)
    def download_shopping_cart(self, request):
        """Добавление рецептов в список покупок."""
        empty_message = 'В списке покупок пусто'
        user = request.user
        if not user.shopcarts.exists():
            return Response({'error': empty_message},
                            status=status.HTTP_204_NO_CONTENT)
        ingredient_list = Amount.objects.filter(
            recipe__shopcarts__user=user
        ).values(
            ingredients=F('ingredient__name'),
            measure_units=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_card.txt'
        shopping_list = (
            f'Список покупок\n\n'
            f'Загрузил пользователь:{user.username}\n'
            f'Создан: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n'
        )
        for ing in ingredient_list:
            shopping_list += (
                f'{ing["ingredients"]} --- '
                f'{ing["amount"]} {ing["measure_units"]}\n'
            )
        shopping_list += ('\nБэкенд проекта разработал Антон Корчагин')
        response = HttpResponse(shopping_list,
                                content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
