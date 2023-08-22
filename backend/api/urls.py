from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet, RecipeViewSet, TagViewSet, IngredientViewSet


router = DefaultRouter()
router.register('users', MyUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')

urlpatterns = (
    path('', include(router.urls)),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
