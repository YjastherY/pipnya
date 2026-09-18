# Связь функций с реализацией

Эта таблица предназначена для переноса в отчёт. После публикации репозитория и деплоя относительные ссылки нужно заменить публичными URL.

| Функция | Код | Страница сайта |
| --- | --- | --- |
| Регистрация и вход | [app/api/auth.py](../app/api/auth.py), [app/static/auth.js](../app/static/auth.js) | `/register`, `/login` |
| Общая лента и поиск | [app/api/posts.py](../app/api/posts.py), [app/static/feed.js](../app/static/feed.js) | `/` |
| Создание записи | [app/api/posts.py](../app/api/posts.py), [app/static/posts.js](../app/static/posts.js) | `/` |
| Изменение и удаление своей записи | [app/api/posts.py](../app/api/posts.py), [app/static/posts.js](../app/static/posts.js) | `/mine` |
| Просмотр профиля и подписка | [app/api/social.py](../app/api/social.py), [app/static/profile.js](../app/static/profile.js) | `/profile/{username}` |
| Лента подписок | [app/api/posts.py](../app/api/posts.py) | `/following` |
| Сохранение записей | [app/api/social.py](../app/api/social.py), [app/static/posts.js](../app/static/posts.js) | `/saved` |
| Схема данных и целостность | [app/schema.sql](../app/schema.sql), [app/db.py](../app/db.py) | `/api/health` |
| Резервное копирование | [app/db.py](../app/db.py) | Команда CLI, в сайте отдельного экрана нет |
