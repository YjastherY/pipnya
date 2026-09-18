# Маяк

«Маяк» — микроблог для коротких заметок. Пользователь может публиковать записи с тегами, искать идеи, подписываться на авторов и сохранять интересные публикации. Проект сделан по теме [Build a Microblog with Flask](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) из [каталога Project Based Learning](https://github.com/practical-tutorials/project-based-learning), с собственной реализацией интерфейса, API и схемы данных.

![Главная страница Маяка с демонстрационными записями](docs/images/home.png)

## Возможности

- Регистрация и вход с хранением хеша пароля.
- Создание, редактирование и удаление своих заметок.
- Теги, поиск и постраничная выдача публикаций.
- Профили авторов и лента подписок.
- Сохранённые заметки.
- Резервное копирование и проверка целостности SQLite.

## Стек

| Слой | Технологии |
| --- | --- |
| Интерфейс | HTML, CSS, JavaScript |
| Сервер и API | Python 3.11+, Flask 3.1 |
| База данных | SQLite 3 |
| Тесты | `unittest`, тестовый клиент Flask |

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app run.py run
```

Откройте `http://127.0.0.1:5000`. База данных создаётся при первом запуске в `instance/microblog.sqlite3`. На Windows используйте `.venv\Scripts\activate` вместо команды `source`.

Для демонстрационных записей и аккаунта `demo` сначала задайте пароль длиной от 10 символов и выполните `flask --app run.py seed-demo`. Пароль берётся из переменной `DEMO_PASSWORD`; команда сообщает только логин, не печатая пароль. Повторный запуск не дублирует записи. Для размещённого сайта этот пароль нужно передать проверяющему в отчёте.

## Проверка и обслуживание

```bash
python -m unittest discover -s tests -v
flask --app run.py check-db
flask --app run.py backup-db backups/microblog.sqlite3
```

Для локальной проверки стиля кода установите `requirements-dev.txt` и выполните `ruff check app tests run.py` и `ruff format --check app tests run.py`. Те же проверки запускаются в GitHub Actions вместе с тестами и проверкой синтаксиса JavaScript.

Для продакшена задайте `APP_ENV=production`, `SECRET_KEY` (случайная длинная строка) и `DATABASE_PATH` (путь на постоянном диске). Пример запуска через WSGI-сервер:

```bash
gunicorn --bind 0.0.0.0:8000 run:app
```

SQLite рассчитана на один экземпляр приложения и постоянный диск. На хостинге с временной файловой системой данные пропадут после перезапуска; для сдачи проекта нужен хостинг с постоянным хранилищем.

Для контейнера есть [Dockerfile](Dockerfile). Подключите постоянный том к `/data`, задайте `SECRET_KEY` и при необходимости `DEMO_PASSWORD`; контейнер заполнит демонстрационные данные и запустит Gunicorn. Без постоянного тома размещение не подходит для проверки сохранения данных.

## Документация

- [Архитектура, ERD и сценарии](docs/architecture.md)
- [Схема и обслуживание БД](docs/database.md)
- [Контракт API](docs/api.md)
- [Связь функций с файлами и страницами](docs/traceability.md)

Репозиторий для публикации: [YjastherY/pipnya](https://github.com/YjastherY/pipnya). Ссылка на деплой и бейдж качества будут добавлены после публикации и проверки работающего сайта.
