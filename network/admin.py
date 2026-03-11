from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import NetworkNode, Contact, Product

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'country', 'city', 'street', 'house_number')
    list_filter = ('country', 'city')
    search_fields = ('email', 'country', 'city')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'release_date')
    list_filter = ('release_date',)
    search_fields = ('name', 'model')

@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'city', 'supplier_link', 'debt', 'created_at')
    list_filter = ('level', 'contact__city', 'contact__country')
    search_fields = ('name', 'contact__email', 'contact__city')
    readonly_fields = ('created_at',)
    filter_horizontal = ('products',)
    actions = ['clear_debt']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'level', 'supplier')
        }),
        ('Контакты', {
            'fields': ('contact',)
        }),
        ('Продукты', {
            'fields': ('products',)
        }),
        ('Финансовая информация', {
            'fields': ('debt',)
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('contact', 'supplier')
    
    def city(self, obj):
        return obj.contact.city if obj.contact else '-'
    city.short_description = 'Город'
    city.admin_order_field = 'contact__city'
    
    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse('admin:network_networknode_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return '-'
    supplier_link.short_description = 'Поставщик'
    
    @admin.action(description='Очистить задолженность перед поставщиком')
    def clear_debt(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(debt=0)
        self.message_user(request, f'Задолженность очищена у {updated} объектов')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
