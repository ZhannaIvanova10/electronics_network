# 🎬 СКРИНКАСТ ПРОЕКТА "Платформа торговой сети электроники"

## 📋 ИНФОРМАЦИЯ О ПРОЕКТЕ
- **Дата выполнения:** 11 марта 2026
- **Автор:** ZhannaIvanova10
- **Репозиторий:** https://github.com/ZhannaIvanova10/electronics_network

## 📁 СОДЕРЖАНИЕ ПАПКИ SCREENCAST

| Файл | Описание |
|------|----------|
| `01_structure.txt` | Структура проекта (вывод `ls -la`) |
| `02_models.txt` | Модели данных и их поля |
| `03_data.txt` | Данные в базе (3 звена сети) |
| `demo_commands.txt` | Полный список команд для демонстрации |
| `README.txt` | Краткое описание скринкаста |

## 📊 СТАТУС ВЫПОЛНЕНИЯ: 20/20

### Технические требования:
- ✅ Python 3.13.3
- ✅ Django 4.2.7
- ✅ DRF 3.14.0
- ✅ PostgreSQL 10+ (настроен в коде)

### Модели данных:
- ✅ Иерархия: Завод (0), Розница (1), ИП (2)
- ✅ Контакты: 5 полей (email, страна, город, улица, дом)
- ✅ Продукты: 3 поля (название, модель, дата)
- ✅ Поставщик (ForeignKey)
- ✅ Задолженность (DecimalField)
- ✅ Время создания (auto_now_add)

### Админ-панель:
- ✅ Вывод всех объектов
- ✅ Ссылка на поставщика
- ✅ Фильтр по городу
- ✅ Action очистки долга

### API:
- ✅ CRUD операции
- ✅ Запрет обновления долга
- ✅ Фильтрация по стране
- ✅ Права доступа (только активные сотрудники)

### Дополнительно:
- ✅ GitHub репозиторий
- ✅ Полная документация

## 🚀 БЫСТРЫЙ ЗАПУСК
```bash
git clone https://github.com/ZhannaIvanova10/electronics_network.git
cd electronics_network
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata network/fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
