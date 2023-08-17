from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet


router = DefaultRouter()
router.register('users', MyUserViewSet, basename='users')

urlpatterns = (
    path('', include(router.urls)),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
