from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Contact(models.Model):
    email = models.EmailField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
    
    def __str__(self):
        return f"{self.email}, {self.city}, {self.street} {self.house_number}"
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    model = models.CharField(max_length=200, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
    
    def __str__(self):
        return f"{self.name} ({self.model})"

class NetworkNode(models.Model):
    class NodeLevel(models.IntegerChoices):
        FACTORY = 0, 'Завод'
        RETAIL = 1, 'Розничная сеть'
        INDIVIDUAL = 2, 'Индивидуальный предприниматель'
    
    name = models.CharField(max_length=255, verbose_name='Название')
    level = models.IntegerField(choices=NodeLevel.choices, verbose_name='Уровень иерархии')
    contact = models.OneToOneField(
        Contact, 
        on_delete=models.CASCADE, 
        related_name='network_node',
        verbose_name='Контакты'
    )
    products = models.ManyToManyField(Product, related_name='network_nodes', verbose_name='Продукты')
    supplier = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='customers',
        verbose_name='Поставщик'
    )
    debt = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Задолженность перед поставщиком'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    
    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
    def __str__(self):
        return f"{self.get_level_display()}: {self.name}"
    
    def save(self, *args, **kwargs):
        # Автоматическое определение уровня на основе поставщика
        if not self.supplier:
            self.level = self.NodeLevel.FACTORY
        elif self.supplier.level == self.NodeLevel.FACTORY:
            self.level = self.NodeLevel.RETAIL
        elif self.supplier.level == self.NodeLevel.RETAIL:
            self.level = self.NodeLevel.INDIVIDUAL
        super().save(*args, **kwargs)
