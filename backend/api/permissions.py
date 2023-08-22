from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AuthorStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    """Изменение объекта только для персонала и автора или только чтение."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method == 'GET'
            or request.user.is_staff
            or (request.user == obj.author)
        )
