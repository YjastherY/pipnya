# Связь функций с реализацией

Таблица содержит точные ссылки на исходный код и страницы размещённого приложения. Её можно использовать как основу раздела «Таблица соответствия» в отчёте.

| Функция | Код | Страница сайта |
| --- | --- | --- |
| Регистрация и вход | [app/api/auth.py](https://github.com/YjastherY/pipnya/blob/main/app/api/auth.py), [app/static/auth.js](https://github.com/YjastherY/pipnya/blob/main/app/static/auth.js) | [Регистрация](https://mayak-yjasthery.vercel.app/register), [вход](https://mayak-yjasthery.vercel.app/login) |
| Общая лента и поиск | [app/api/posts.py](https://github.com/YjastherY/pipnya/blob/main/app/api/posts.py), [app/static/feed.js](https://github.com/YjastherY/pipnya/blob/main/app/static/feed.js) | [Главная страница](https://mayak-yjasthery.vercel.app/) |
| Создание записи | [app/api/posts.py](https://github.com/YjastherY/pipnya/blob/main/app/api/posts.py), [app/static/posts.js](https://github.com/YjastherY/pipnya/blob/main/app/static/posts.js) | [Главная страница](https://mayak-yjasthery.vercel.app/) |
| Изменение и удаление своей записи | [app/api/posts.py](https://github.com/YjastherY/pipnya/blob/main/app/api/posts.py), [app/static/posts.js](https://github.com/YjastherY/pipnya/blob/main/app/static/posts.js) | [Мои заметки](https://mayak-yjasthery.vercel.app/mine) |
| Просмотр профиля и подписка | [app/api/social.py](https://github.com/YjastherY/pipnya/blob/main/app/api/social.py), [app/static/profile.js](https://github.com/YjastherY/pipnya/blob/main/app/static/profile.js) | [Профиль demo](https://mayak-yjasthery.vercel.app/profile/demo) |
| Лента подписок | [app/api/posts.py](https://github.com/YjastherY/pipnya/blob/main/app/api/posts.py) | [Подписки](https://mayak-yjasthery.vercel.app/following) |
| Сохранение записей | [app/api/social.py](https://github.com/YjastherY/pipnya/blob/main/app/api/social.py), [app/static/posts.js](https://github.com/YjastherY/pipnya/blob/main/app/static/posts.js) | [Сохранённое](https://mayak-yjasthery.vercel.app/saved) |
| Схема данных и целостность | [app/schema.sql](https://github.com/YjastherY/pipnya/blob/main/app/schema.sql), [app/db.py](https://github.com/YjastherY/pipnya/blob/main/app/db.py) | [Проверка состояния](https://mayak-yjasthery.vercel.app/api/health) |
| Резервное копирование | [app/db.py](https://github.com/YjastherY/pipnya/blob/main/app/db.py) | Команда `flask --app run.py backup-db` |
