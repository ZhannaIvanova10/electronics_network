from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import NetworkNode, Contact, Product
from decimal import Decimal

User = get_user_model()


class ContactModelTest(TestCase):
    """Тесты для модели Contact"""

    def setUp(self):
        self.contact = Contact.objects.create(
            email="test@example.com",
            country="Россия",
            city="Москва",
            street="Ленина",
            house_number="10"
        )

    def test_contact_creation(self):
        """Тест создания контакта"""
        self.assertEqual(self.contact.email, "test@example.com")
        self.assertEqual(self.contact.country, "Россия")
        self.assertEqual(self.contact.city, "Москва")
        self.assertEqual(self.contact.street, "Ленина")
        self.assertEqual(self.contact.house_number, "10")

    def test_contact_str_method(self):
        """Тест строкового представления"""
        expected = "test@example.com, Москва, Ленина 10"
        self.assertEqual(str(self.contact), expected)

    def test_contact_fields_count(self):
        """Проверка количества полей (должно быть 5)"""
        fields = [f.name for f in Contact._meta.fields if f.name != 'id']
        self.assertEqual(len(fields), 5)
        self.assertIn('email', fields)
        self.assertIn('country', fields)
        self.assertIn('city', fields)
        self.assertIn('street', fields)
        self.assertIn('house_number', fields)


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        self.product = Product.objects.create(
            name="Смартфон",
            model="X100",
            release_date="2024-01-15"
        )
    def test_product_creation(self):
        """Тест создания продукта"""
        self.assertEqual(self.product.name, "Смартфон")
        self.assertEqual(self.product.model, "X100")
        self.assertEqual(self.product.release_date, "2024-01-15")

    def test_product_str_method(self):
        """Тест строкового представления"""
        expected = "Смартфон (X100)"
        self.assertEqual(str(self.product), expected)

    def test_product_fields_count(self):
        """Проверка количества полей (должно быть 3)"""
        fields = [f.name for f in Product._meta.fields if f.name != 'id']
        self.assertEqual(len(fields), 3)
        self.assertIn('name', fields)
        self.assertIn('model', fields)
        self.assertIn('release_date', fields)


class NetworkNodeModelTest(TestCase):
    """Тесты для модели NetworkNode"""

    def setUp(self):
        # Создаем контакты
        self.contact1 = Contact.objects.create(
            email="factory@example.com",
            country="Россия",
            city="Москва",
            street="Заводская",
            house_number="1"
        )
        self.contact2 = Contact.objects.create(
            email="retail@example.com",
            country="Россия",
            city="СПб",
            street="Невский",
            house_number="25"
        )
        # Создаем продукты
        self.product1 = Product.objects.create(
            name="Смартфон",
            model="X100",
            release_date="2024-01-15"
        )
        self.product2 = Product.objects.create(
            name="Ноутбук",
            model="ProBook",
            release_date="2024-02-20"
        )

        # Создаем звенья сети
        self.factory = NetworkNode.objects.create(
            name="Тестовый завод",
            contact=self.contact1,
            debt=Decimal('0.00')
        )
        self.factory.products.set([self.product1.id, self.product2.id])

        self.retail = NetworkNode.objects.create(
            name="Тестовый магазин",
            contact=self.contact2,
            supplier=self.factory,
            debt=Decimal('150000.50')
        )
        self.retail.products.set([self.product1.id])

    def test_factory_creation(self):
        """Тест создания завода (уровень 0)"""
        self.assertEqual(self.factory.name, "Тестовый завод")
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.factory.get_level_display(), "Завод")
        self.assertIsNone(self.factory.supplier)
        self.assertEqual(self.factory.debt, Decimal('0.00'))

    def test_retail_creation(self):
        """Тест создания розничной сети (уровень 1)"""
        self.assertEqual(self.retail.name, "Тестовый магазин")
        self.assertEqual(self.retail.level, 1)
        self.assertEqual(self.retail.get_level_display(), "Розничная сеть")
        self.assertEqual(self.retail.supplier, self.factory)
        self.assertEqual(self.retail.debt, Decimal('150000.50'))

    def test_auto_level_assignment(self):
        """Тест автоматического определения уровня"""
        # Создаем ИП с поставщиком-розницей
        contact3 = Contact.objects.create(
            email="ip@example.com",
            country="Россия",
            city="Казань",
            street="Баумана",
            house_number="15"
        )
        ip = NetworkNode.objects.create(
            name="Тестовый ИП",
            contact=contact3,
            supplier=self.retail,
            debt=Decimal('50000.75')
        )
        self.assertEqual(ip.level, 2)
        self.assertEqual(ip.get_level_display(), "Индивидуальный предприниматель")

    def test_products_relation(self):
        """Тест связи с продуктами"""
        self.assertEqual(self.factory.products.count(), 2)
        self.assertEqual(self.retail.products.count(), 1)
        self.assertIn(self.product1, self.factory.products.all())
        self.assertIn(self.product2, self.factory.products.all())

    def test_str_method(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.factory), "Завод: Тестовый завод")
        self.assertEqual(str(self.retail), "Розничная сеть: Тестовый магазин")


class NetworkNodeAPITest(APITestCase):
    """Тесты для API"""

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_active=True
        )
        self.client = APIClient()

        # Создаем тестовые данные
        self.contact = Contact.objects.create(
            email="api@test.com",
            country="Россия",
            city="Москва",
            street="Тестовая",
            house_number="1"
        )
        self.factory = NetworkNode.objects.create(
            name="API Завод",
            contact=self.contact,
            debt=Decimal('0.00')
        )

    def test_api_unauthenticated(self):
        """Тест доступа без авторизации (должен быть 403)"""
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_authenticated(self):
        """Тест доступа с авторизацией (должен быть 200)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_create_node(self):
        """Тест создания узла через API"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Новый магазин",
            "contact": {
                "email": "new@shop.com",
                "country": "Россия",
                "city": "Новосибирск",
                "street": "Главная",
                "house_number": "100"
            },
            "product_ids": [],
            "supplier_id": self.factory.id
        }
        response = self.client.post('/api/nodes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkNode.objects.count(), 2)
    def test_api_debt_read_only(self):
        """Тест запрета обновления долга через API"""
        self.client.force_authenticate(user=self.user)
        data = {"debt": "999999.99"}
        response = self.client.patch(f'/api/nodes/{self.factory.id}/', data, format='json')
        self.factory.refresh_from_db()
        self.assertEqual(self.factory.debt, Decimal('0.00'))  # Долг не изменился

    def test_api_filter_by_country(self):
        """Тест фильтрации по стране"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/nodes/?country=Россия')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NetworkNodeAdminTest(TestCase):
    """Тесты для админ-панели"""

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        # Создаем тестовые данные для админки
        self.contact = Contact.objects.create(
            email="admin@test.com",
            country="Россия",
            city="Москва",
            street="Админская",
            house_number="1"
        )
        self.product = Product.objects.create(
            name="Тестовый продукт",
            model="TestModel",
            release_date="2024-01-01"
        )
        self.node = NetworkNode.objects.create(
            name="Тестовый узел",
            contact=self.contact,
            debt=Decimal('1000.00')
        )
        self.node.products.set([self.product.id])
        self.client.force_login(self.user)

    def test_admin_login(self):
        """Тест доступа к админке"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Администрирование')

    def test_admin_networknode_list(self):
        """Тест отображения списка узлов в админке"""
        response = self.client.get('/admin/network/networknode/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый узел')
        self.assertContains(response, 'Задолженность')

    def test_admin_contact_list(self):
        """Тест отображения списка контактов в админке"""
        response = self.client.get('/admin/network/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin@test.com')
        self.assertContains(response, 'Москва')

    def test_admin_product_list(self):
        """Тест отображения списка продуктов в админке"""
        response = self.client.get('/admin/network/product/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый продукт')
        self.assertContains(response, 'TestModel')

    def test_admin_networknode_detail(self):
        """Тест детальной страницы узла"""
        response = self.client.get(f'/admin/network/networknode/{self.node.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый узел')
        self.assertContains(response, 'Задолженность')

class PermissionsTest(APITestCase):
    """Тесты для прав доступа"""

    def setUp(self):
        # Активный сотрудник
        self.active_staff = User.objects.create_user(
            username='active_staff',
            password='pass123',
            is_staff=True,
            is_active=True
        )
        # Неактивный сотрудник
        self.inactive_staff = User.objects.create_user(
            username='inactive_staff',
            password='pass123',
            is_staff=True,
            is_active=False
        )
        # Обычный пользователь
        self.normal_user = User.objects.create_user(
            username='normal',
            password='pass123',
            is_staff=False,
            is_active=True
        )
        self.client = APIClient()

    def test_active_staff_access(self):
        """Активный сотрудник должен иметь доступ"""
        self.client.force_authenticate(user=self.active_staff)
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inactive_staff_no_access(self):
        """Неактивный сотрудник не должен иметь доступ"""
        self.client.force_authenticate(user=self.inactive_staff)
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_no_access(self):
        """Обычный пользователь не должен иметь доступ"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class PaginationTest(APITestCase):
    """Тесты для пагинации"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='pagination_user',
            password='test123',
            is_staff=True,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Создаем 15 тестовых узлов
        for i in range(15):
            contact = Contact.objects.create(
                email=f"test{i}@test.com",
                country="Россия",
                city=f"Город{i}",
                street="Тестовая",
                house_number=str(i)
            )
            NetworkNode.objects.create(
                name=f"Тестовый узел {i}",
                contact=contact,
                debt=Decimal(f"{i}00.00")
            )
    
    def test_default_pagination(self):
        """Тест пагинации по умолчанию (page_size=10)"""
        response = self.client.get('/api/nodes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)
    def test_custom_page_size(self):
        """Тест кастомного размера страницы"""
        response = self.client.get('/api/nodes/?page_size=5')
        self.assertEqual(len(response.data['results']), 5)
    
    def test_second_page(self):
        """Тест второй страницы"""
        response = self.client.get('/api/nodes/?page=2&page_size=5')
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['previous'], 'http://testserver/api/nodes/?page=1&page_size=5')


class SortingTest(APITestCase):
    """Тесты для сортировки"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='sort_user',
            password='test123',
            is_staff=True,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_sort_by_name(self):
        """Тест сортировки по имени"""
        response = self.client.get('/api/nodes/?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sort_by_debt_desc(self):
        """Тест сортировки по долгу (убывание)"""
        response = self.client.get('/api/nodes/?ordering=-debt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_sort_by_created_at(self):
        """Тест сортировки по дате создания"""
        response = self.client.get('/api/nodes/?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdvancedFilterTest(APITestCase):
    """Тесты для расширенной фильтрации"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='filter_user',
            password='test123',
            is_staff=True,
            is_active=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_filter_min_debt(self):
        """Тест фильтрации по минимальному долгу"""
        response = self.client.get('/api/nodes/?min_debt=100000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_max_debt(self):
        """Тест фильтрации по максимальному долгу"""
        response = self.client.get('/api/nodes/?max_debt=50000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_city_contains(self):
        """Тест фильтрации по части названия города"""
        response = self.client.get('/api/nodes/?city_contains=Моск')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
