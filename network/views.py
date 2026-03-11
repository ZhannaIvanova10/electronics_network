from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkNode
from .serializers import NetworkNodeSerializer
import django_filters

class NetworkNodeFilter(django_filters.FilterSet):
    """Расширенный фильтр для NetworkNode"""
    min_debt = django_filters.NumberFilter(field_name='debt', lookup_expr='gte')
    max_debt = django_filters.NumberFilter(field_name='debt', lookup_expr='lte')
    city_contains = django_filters.CharFilter(field_name='contact__city', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='contact__country', lookup_expr='exact')
    level = django_filters.NumberFilter(field_name='level')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = NetworkNode
        fields = ['level', 'contact__country', 'contact__city', 'debt']


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.is_staff)


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели NetworkNode с CRUD операциями
    Поддерживает:
    - Пагинацию (page, page_size)
    - Сортировку (ordering=name, -debt, created_at)
    - Фильтрацию (country, level, min_debt, max_debt, city_contains)
    - Поиск (search=название)
    """
    queryset = NetworkNode.objects.all().select_related('contact').prefetch_related('products')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NetworkNodeFilter
    search_fields = ['name', 'contact__city', 'contact__country', 'contact__email']
    ordering_fields = ['name', 'created_at', 'debt', 'level']
    ordering = ['name']  # Сортировка по умолчанию
    def get_queryset(self):
        """
        Опциональная фильтрация по стране (для обратной совместимости)
        """
        queryset = super().get_queryset()
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(contact__country=country)
        return queryset
