# Transaction Service

## Описание

Transaction Service — это приложение, предоставляющее функциональность для управления транзакциями между пользователями. Оно включает регистрацию пользователей, аутентификацию, а также создание и получение транзакций.

## Стек технологий
- **FastAPI**: веб-фреймворк для создания API.
- **SQLAlchemy**: ORM для работы с базой данных.
- **PostgreSQL**: реляционная база данных.
- **Alembic**: инструмент для миграции базы данных.
- **Pydantic**: библиотека для валидации данных.
- **JWT**: для аутентификации пользователей.

---

## Установка

### Предварительные требования
- Python 3.8 или выше
- Docker и Docker Compose

### Клонирование репозитория
```bash
git clone https://github.com/skv43r/transaction_service.git
cd transaction_service
```

### Настройка окружения

1. Создайте файл `.env` в корне кажого сервиса, где есть sample.env и добавьте следующие переменные:
   ```dotenv
   DATABASE_URL=postgresql+asyncpg://<login>:<password>@<host>:<port>/<db_name>
   JWT_SECRET=<secret_key>
   ```

2. Убедитесь, что Docker и Docker Compose установлены и запущены.

---

## Запуск приложения

1. Запустите контейнеры с помощью Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. После запуска контейнеров выполните миграции базы данных:
   ```bash
   cd common
   alembic upgrade head
   ```

Приложение будет доступно по следующим адресам:
- **Аутентификация**: [http://localhost:8001/auth](http://localhost:8001/auth)
- **Транзакции**: [http://localhost:8002/transactions](http://localhost:8002/transactions)

---

## Использование API

### Регистрация пользователя
**POST /auth/register**

Тело запроса:
```json
{
  "username": "new_user",
  "email": "new_user@example.com",
  "password": "strongpassword"
}
```

### Вход пользователя
**POST /auth/login**

Тело запроса:
```json
{
  "username": "new_user",
  "password": "strongpassword"
}
```

### Создание транзакции
**POST /transactions/transfer**

Тело запроса:
```json
{
  "receiver_id": 1,
  "amount": 100.0
}
```

### Получение транзакций
**GET /transactions**

Параметры запроса:
- `skip`: количество пропускаемых транзакций (по умолчанию 0)
- `limit`: максимальное количество возвращаемых транзакций (по умолчанию 10)

---

## Миграции базы данных
Для применения миграций используйте Alembic. Команды для миграции:

```bash
alembic upgrade head
```

---

## Логирование
Логи приложения записываются в файл `app.log`.

---

## Заключение
Transaction Service предоставляет базовую функциональность для управления пользователями и транзакциями.

