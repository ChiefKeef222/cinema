# Cinema

Проект Cinema — это система для управления фильмами, залами, сеансами и бронированием мест.  
Написан на Django REST Framework с использованием PostgreSQL, Redis и Docker. Подключен Swagger для удобной работы с API.

---

## Цель проекта

- Обеспечить полный CRUD для фильмов, залов и сеансов.  
- Реализовать бронирование мест с обновлением через WebSocket.  
- Дать разработчику и клиенту простой и прозрачный API.  

---

## Быстрый старт

1. Склонируйте репозиторий:

```bash
git clone https://github.com/ChiefKeef222/cinema.git
cd cinema
```

2.Создайте .env файл по образцу:
```env
Копировать код
DEBUG=True
SECRET_KEY=your_secret_key
POSTGRES_DB=cinema
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
```

3.Запустите Docker:
```bash
docker-compose up --build
```

4.Откройте Swagger на:
```
http://localhost:8000/swagger/ (основной)
http://localhost:8000/docs/ (альтернатива)
```

Функционал
```Пользователи:
POST /auth/register/ — регистрация пользователя
POST /auth/login/ — вход пользователя
POST /auth/refresh/ — обновление JWT

Фильмы:
GET /movies/ — список фильмов
GET /movies/{id}/ — конкретный фильм
POST /movies/ — создать фильм
PUT /movies/{id}/, PATCH /movies/{id}/ — обновить данные
DELETE /movies/{id}/ — удалить фильм

Залы и сеансы:
GET /hall/ — список залов
GET /session/ — список сеансов
POST /hall/, POST /session/ — создание залов/сеансов
PATCH /hall/{id}/, PUT/PATCH /session/{id}/ — обновление
GET /hall/{id}/, GET /session/{id}/ — детали
DELETE /hall/{id}/, DELETE /session/{id}/ — удалить
GET /sessions/{session_id}/seats/ — забронированные места

Бронирование:
GET /bookings/ — просмотр бронирований
POST /bookings/ — создать бронирование
ws://session/<uuid:session_id>/seats/ — WebSocket для обновления схемы залов в реальном времени
```
Демо-данные
 - 3 фильма
 - 2 зала
 - 3 сеанса

Файл с демо-данными доступен: demo_data.sql
Пример загрузки SQL:
```bash
psql -U postgres -d cinema -f demo_data.sql
```

CI/CD
Проект настроен на автоматический билд и деплой через Docker/GitHub Actions или GitLab CI.
Все тесты проходят перед деплоем.

Стек технологий
 - Python, Django, Django REST Framework
 - PostgreSQL
 - Redis
 - Docker
 - Swagger / drf-yasg
