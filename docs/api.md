# API

Все изменяющие запросы передают JSON и заголовок `X-CSRF-Token`. Токен можно получить через `GET /api/session`. При ошибке API возвращает JSON вида `{"error":"Описание"}` и подходящий HTTP-статус.

| Метод | URL | Назначение |
| --- | --- | --- |
| GET | `/api/session` | Текущий пользователь и CSRF-токен |
| POST | `/api/register` | Регистрация |
| POST | `/api/login` | Вход |
| POST | `/api/logout` | Выход |
| GET | `/api/posts` | Лента, поиск, теги и пагинация |
| POST | `/api/posts` | Создание заметки |
| PATCH | `/api/posts/{id}` | Изменение своей заметки |
| DELETE | `/api/posts/{id}` | Удаление своей заметки |
| GET | `/api/users/{username}` | Профиль и счётчики |
| POST/DELETE | `/api/users/{username}/follow` | Подписка и отписка |
| POST/DELETE | `/api/posts/{id}/bookmark` | Добавить/убрать закладку |
| GET | `/api/tags` | Популярные теги |
| GET | `/api/health` | Проверка доступности БД |

`GET /api/posts` принимает `feed=all|following|mine|saved`, `q`, `tag`, `author` и `page`. Размер страницы — 10 записей.

Пример создания заметки:

```json
{"body":"Изучаю реляционные связи в SQLite","tags":["sqlite","study"]}
```

Пример ответа:

```json
{"post":{"id":1,"author_id":1,"username":"demo","body":"Изучаю реляционные связи в SQLite","tags":["sqlite","study"],"bookmarked":false,"created_at":"2026-09-18T08:00:00.000Z","updated_at":null}}
```
