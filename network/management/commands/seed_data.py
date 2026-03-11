from django.core.management.base import BaseCommand
from network.models import Contact, Product, NetworkNode
from decimal import Decimal
import random
from faker import Faker

fake = Faker('ru_RU')

class Command(BaseCommand):
    help = 'Генерирует тестовые данные для проекта'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Количество генерируемых узлов')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Генерация {count} тестовых узлов...')

        # Создаем продукты
        products = []
        product_names = ['Смартфон', 'Ноутбук', 'Планшет', 'Телевизор', 'Наушники', 
                        'Монитор', 'Клавиатура', 'Мышь', 'Принтер', 'Колонки']
        
        for i in range(10):
            product = Product.objects.create(
                name=product_names[i],
                model=fake.bothify(text='??###'),
                release_date=fake.date_between(start_date='-2y', end_date='today')
            )
            products.append(product)
            self.stdout.write(f'  Создан продукт: {product.name} ({product.model})')
        # Создаем заводы (уровень 0)
        factories = []
        for i in range(5):
            contact = Contact.objects.create(
                email=fake.email(),
                country='Россия',
                city=fake.city(),
                street=fake.street_name(),
                house_number=fake.building_number()
            )
            factory = NetworkNode.objects.create(
                name=f"Завод «{fake.company()}»",
                contact=contact,
                debt=Decimal('0.00')
            )
            factory.products.set(random.sample(products, random.randint(3, 7)))
            factories.append(factory)
            self.stdout.write(f'  Создан завод: {factory.name}')

        # Создаем розничные сети (уровень 1)
        retails = []
        for i in range(15):
            contact = Contact.objects.create(
                email=fake.email(),
                country='Россия',
                city=fake.city(),
                street=fake.street_name(),
                house_number=fake.building_number()
            )
            supplier = random.choice(factories)
            retail = NetworkNode.objects.create(
                name=f"«{fake.company()}» (розница)",
                contact=contact,
                supplier=supplier,
                debt=Decimal(str(random.randint(10000, 500000) / 100))
            )
            retail.products.set(random.sample(products, random.randint(2, 5)))
            retails.append(retail)
            self.stdout.write(f'  Создана розничная сеть: {retail.name} (поставщик: {supplier.name})')
        # Создаем ИП (уровень 2)
        for i in range(count - 20):  # Остальные - ИП
            contact = Contact.objects.create(
                email=fake.email(),
                country='Россия',
                city=fake.city(),
                street=fake.street_name(),
                house_number=fake.building_number()
            )
            supplier = random.choice(retails + factories)
            ip = NetworkNode.objects.create(
                name=f"ИП {fake.last_name()}",
                contact=contact,
                supplier=supplier,
                debt=Decimal(str(random.randint(1000, 100000) / 100))
            )
            ip.products.set(random.sample(products, random.randint(1, 3)))
            self.stdout.write(f'  Создан ИП: {ip.name} (поставщик: {supplier.name})')

        self.stdout.write(self.style.SUCCESS(f'✅ Успешно создано {NetworkNode.objects.count()} узлов сети!'))
