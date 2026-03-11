from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkNode
from .serializers import NetworkNodeSerializer

class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.is_staff)

class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели NetworkNode с CRUD операциями
    """
    queryset = NetworkNode.objects.all().select_related('contact').prefetch_related('products')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact__country', 'level']
    search_fields = ['name', 'contact__city', 'contact__country']
    ordering_fields = ['name', 'created_at', 'debt']
    
    def get_queryset(self):
        """
        Опциональная фильтрация по стране
        """
        queryset = super().get_queryset()
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(contact__country=country)
        return queryset
