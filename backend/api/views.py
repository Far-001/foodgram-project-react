from datetime import datetime

from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
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

from users.models import MyUser, Follow
from app.models import Ingredient, Amount, Recipe, Tag

from .serializers import MyUserSerializer, FollowSerializer


class MyUserViewSet(UserViewSet):
    """
    Вьюсет для работы с пользователями.
    Доступ для всех.
    """
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [AllowAny]
    add_serializer = FollowSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Выдает подписки для авторизванных пользователей"""
        authors = Follow.objects.filter(user=request.user)
        pages = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписка, отписка от автора для авторизованных пользователей."""
        user = self.request.user
        author = get_object_or_404(MyUser, id=id)
        subscription = Follow.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': 'Уже подписаны!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(author, context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не подписаны!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
