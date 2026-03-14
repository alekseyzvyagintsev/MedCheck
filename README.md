# MedCheck - Сайт медицинской диагностики

## Описание проекта

MedCheck - это веб-приложение для медицинской диагностической компании, реализованное с использованием Django и Bootstrap. Проект предоставляет полный функционал для управления медицинскими услугами, записями пациентов и администрированием контента.

## Функционал сайта

### Основные страницы:
- **Главная страница**: Описание компании, перечень услуг, контактная информация
- **О компании**: История компании, миссия и ценности, команда врачей
- **Услуги**: Перечень и подробное описание медицинских услуг с ценами
- **Контакты**: Адрес, карта проезда, телефоны, email, форма обратной связи
- **Личный кабинет**: Регистрация, авторизация, запись на прием, просмотр истории

### Админка Django
- Управление пользователями
- Управление услугами
- Управление записями на прием
- Управление контентом сайта

## Технические требования

### Фреймворк
- Django 6.0.3

### База данных
- PostgreSQL (через psycopg2-binary)

### Фронтенд
- Bootstrap 5 для адаптивного интерфейса
- Кастомные CSS стили с цветовой схемой: бирюзовый (#00c4cc), коралловый (#ff6b6b), белый

### Дополнительные зависимости
- python-decouple - для управления конфигурацией

## Структура проекта

```
MedCheck/
├── manage.py
├── MedCheck/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── main/                  # Главное приложение
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── services/             # Приложение для услуг
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── accounts/             # Приложение для аккаунтов
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── templates/            # Шаблоны
│   └── base.html
├── static/               # Статические файлы
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── images/
├── pyproject.toml        # Управление зависимостями через Poetry
├── poetry.lock
└── README.md
```

## Установка и запуск

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd MedCheck
```

2. Установить зависимости:
```bash
poetry install
```

3. Активировать виртуальное окружение:
```bash
poetry shell
```

4. Настроить переменные окружения (создать файл .env в корне проекта):
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=medcheck
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

5. Применить миграции:
```bash
python manage.py migrate
```

6. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустить сервер:
```bash
python manage.py runserver
```

Проект будет доступен по адресу http://127.0.0.1:8000
Админка доступна по адресу: http://localhost:8000/admin
Учетные данные суперпользователя: username: admin, password: admin

## Контейнеризация (Docker)

Для запуска в Docker:

1. Создать файл `Dockerfile`:
```dockerfile
FROM python:3.12

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install "poetry==1.7.1" && \
    poetry config virtualenvs.create false && \
    poetry export -f requirements.txt --output requirements.txt && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

2. Создать файл `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
    environment:
      - DEBUG=True
      - DB_HOST=db
      - DB_PORT=5432

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

volumes:
  postgres_data:
```

3. Запустить контейнеры:
```bash
docker-compose up --build
```

## Качество кода

- Соблюдение стандартов PEP8
- Код хранится в удаленном Git репозитории
- Адаптивный дизайн с использованием Bootstrap

## Цветовая схема

- Основной цвет (бирюзовый): #00c4cc
- Вторичный цвет (коралловый): #ff6b6b
- Фоновый цвет (белый): #ffffff

Разработано для компании медицинской диагностики с акцентом на современный, профессиональный и дружелюбный интерфейс.