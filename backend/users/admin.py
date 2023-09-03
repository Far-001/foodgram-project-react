from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Follow, MyUser


class MyUserAdmin(UserAdmin):
    """Кастомное отображение модели User а админке."""
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('email', 'first_name')
    search_fields = ('username', 'email')
    empty_value_display = '-нет-'


site.unregister(Group)
site.register(MyUser, MyUserAdmin)
site.register(Follow)
