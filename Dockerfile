FROM python:3.13-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копирование проекта
COPY . .

# Сбор статических файлов
RUN python manage.py collectstatic --noinput

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
