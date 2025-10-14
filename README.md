# Cadastrals

## Описание

Сервис, который принимает запрос с указанием кадастрового номера, широты и долготы, эмулирует отправку запроса на внешний сервер, который может обрабатывать запрос до 60 секунд. Затем внешний сервер отдаёт результат запроса. Считается, что внешний сервер может ответить True или False. Данные запроса на сервер и ответ с внешнего сервера сохраняются в БД.



## Развертывание через Docker Compose

### 1. Клонирование репозитория

```bash
git clone git@github.com:Enigmatica33/cadastrals.git
cd cadastrals
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта со следующим содержимым:

```bash
# PostgreSQL настройки
DATABASE_URL="подключение к postgres через asyncpg"
DATABASE_URL_ALEMBIC="подключение к postgres через psycopg2 для миграций alembic"
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=postgres_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```


### 3. Запуск системы

```bash
# Запуск сервиса
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка сервиса
docker compose down
```


**Ожидаемый результат:**
- PostgreSQL: контейнер `cadastrals_postgres` в состоянии `Up (healthy)`
- Приложение: контейнер `cadastrals_app` в состоянии `Up (Started)`

### 4. Доступ к сервисам

- **openapi.json**: http://127.1.0.0:8000/docs

## Архитектура системы

### Сервисы Docker Compose

- **postgres**: PostgreSQL 15-alpine
  - Порт: 5432
  - Данные: volume `postgres_data`
  - Health check: каждые 10 секунд

- **cadastrals_app**: Приложение на FastAPI
  - Автоперезапуск: unless-stopped
  - Зависимость: postgres (healthy)

### Сетевая конфигурация

- Изолированная сеть: `cadastrals_network`
- Тип сети: bridge
- Внутренние имена хостов совпадают с именами сервисов

### Volumes

- `postgres_data`: постоянное хранение данных PostgreSQL


## Tech Stack
- **Python 3.12+** - основной язык разработки
- **FastAPI 0.118.0** - основной веб-фреймворк
- **SQLAlchemy 2.0.43** - работа с БД
- **Alembic 1.16.5** - управление миграциями БД
- **PostgreSQL** - основная база данных
- **AsyncPG** - асинхронный драйвер PostgreSQL
