# 👨‍🌾 АгроПочта (AgroMail) ✉️

**АгроПочта** — это учебный веб-сервис для управления email-рассылками, созданный в рамках курсовой работы.  
Проект позволяет фермерам и агробизнесу создавать базы клиентов, готовить шаблоны сообщений и запускать 
персонализированные рассылки с отслеживанием статистики.

---

## 🚀 Основной функционал

- **Управление клиентами** — добавление, просмотр, редактирование и удаление получателей (Email, Ф.И.О., комментарий).
- **Управление сообщениями** — создание шаблонов писем (тема, тело письма).
- **Управление рассылками** — настройка времени начала и окончания, выбор сообщения и списка получателей.
- **Динамический статус** — статус автоматически пересчитывается при открытии страницы 
(`Создана`, `Запущена`, `Завершена`).
- **Ручная отправка** — запуск рассылки по кнопке с проверкой временного интервала. Письма отправляются через 
`send_mail()` (в dev-режиме — в консоль).
- **История попыток** — для каждого письма создаётся запись (Успешно/Не успешно) с ответом сервера. 
Создание через `bulk_create` (batch).
- **Аутентификация** — регистрация с **подтверждением email**, вход/выход, **восстановление пароля**, редактирование 
профиля (с аватаром, районом, городом).
- **Роли и права** — пользователь видит только свои данные; менеджер видит всё, но не может редактировать чужое.
- **Статистика** — отдельная страница с количеством успешных/неуспешных попыток и списком последних отправок.
- **Кэширование** — серверное (Redis) для счётчиков и списков, клиентское (`Cache-Control`).
- **Адаптивная вёрстка** — Bootstrap 5 в зелёно-голубой теме с элементами аграрного дизайна.

---

## 🛠 Технологический стек

- **Python 3.12** — язык программирования.
- **Django 6.1.1** — веб-фреймворк.
- **PostgreSQL 17** — база данных (через `psycopg2-binary`).
- **Redis 7** — сервер кэширования (через Docker).
- **django-redis** — бэкенд кэширования.
- **Docker / Docker Compose** — контейнеризация Redis.
- **Bootstrap 5** — стилизация и адаптивность (CDN).
- **django.core.mail** — отправка писем (консольный backend в dev-режиме).
- **AbstractUser + UserManager** — кастомная модель пользователя.
- **django.test.TestCase** — unit-тесты (13 шт.).
- **Pillow** — работа с изображениями (аватары).

---

## 📦 Установка и запуск

### 1. Клонируйте репозиторий:

```bash
git clone https://github.com/BUMbiro/AgroMail.git
cd AgroMail
```

### 2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### 4. Создайте базу данных PostgreSQL
**В `psql` под суперпользователем postgres:**

```sql
CREATE USER agromail_user WITH PASSWORD 'ваш_пароль';
ALTER USER agromail_user CREATEDB;
CREATE DATABASE agromail WITH OWNER = agromail_user ENCODING = 'UTF8';
```

### 5. Запустите Redis через Docker Compose
```bash
docker compose up -d
```
**Проверка, что `Redis` работает:**

```bash
docker exec -it agromail-redis redis-cli ping
```

**Ожидаем: `PONG`.**

**Остановить Redis:**

```bash
docker compose down
```
### 6. Настройте переменные окружения
**Скопируйте `.env.template` в `.env` и заполните:**

```bash
cp .env.template .env    # Windows: copy .env.template .env
```
**Пример содержимого `.env`:**

```env
SECRET_KEY=ваш_секретный_ключ
DEBUG=True

DB_NAME=agromail
DB_USER=agromail_user
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6380/1
```
>.env добавлен в .gitignore — реальные пароли в репозиторий не попадают.
>В .env.template только заглушки.

### 7. Выполните миграции базы данных:
```bash
python manage.py migrate
```

### 8. Создайте суперпользователя для доступа в админку:
```bash
python manage.py createsuperuser
```
>Важно: `Django` спросит `Email` (а не `username`), потому что в проекте используется кастомная модель 
>`User с USERNAME_FIELD = 'email'`.

### 9. Создайте группу «Менеджер»:
```bash
python manage.py create_manager_group
```
### 10. Запустите сервер:
```bash
python manage.py runserver
```

**Откройте браузер по адресу:**

👉 http://127.0.0.1:8000/

---

## 📁 Структура проекта

```text
AgroMail/
├── accounts/                             # Приложение пользователей
│   ├── migrations/
│   ├── admin.py                          # Админка User (с подтверждением email)
│   ├── forms.py                          # RegisterForm, LoginForm, ProfileForm
│   ├── managers.py                       # UserManager (создание по email)
│   ├── models.py                         # User (AbstractUser, is_email_verified, region, city)
│   ├── tokens.py                         # Генератор токенов для подтверждения email
│   ├── urls.py                           # register / login / logout / profile / verify
│   └── views.py                          # CBV для аутентификации и профиля
├── mailing/                              # Приложение рассылок
│   ├── management/commands/
│   │   └── create_manager_group.py       # Создание группы «Менеджер»
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py                          # Формы для клиентов, сообщений, рассылок
│   ├── models.py                         # Client, Message, Mailing, MailingAttempt
│   ├── services.py                       # Сервис отправки рассылки (send_mailing)
│   ├── urls.py
│   └── views.py                          # CBV (CRUD, отправка, статистика)
├── config/                               # Настройки проекта
│   ├── settings.py                       # PostgreSQL, .env, CACHES (Redis)
│   └── urls.py
├── templates/                            # Шаблоны HTML
│   ├── accounts/                         # login, register, profile, verify
│   ├── mailing/                          # CRUD, статистика, главная
│   └── base.html                         # Базовый шаблон (Bootstrap 5)
├── .env                                  # Переменные (не в git)
├── .env.template                         # Шаблон .env
├── docker-compose.yml                    # Redis-контейнер
├── manage.py
├── README.md
└── requirements.txt
```

---

## 🗄 Модели

**Пользователи**
- `User (AbstractUser) – email (USERNAME_FIELD), password, username, first_name, last_name, avatar, phone_number, 
country, region, city, is_email_verified, is_active, is_staff, date_joined.`
  - Property `is_manager` — проверка, состоит ли пользователь в группе «Менеджер».

**Рассылки**
- `Client – email (уникальный), full_name, comment, owner (FK → User), created_at.` Получатель рассылки.
- `Message – subject, body, owner (FK → User), created_at.` Шаблон письма.
- `Mailing – start_time, end_time, status, message (FK → Message), recipients (M2M → Client), owner (FK → User), 
created_at.` Рассылка.
  - Метод `update_status()` — динамический пересчёт статуса.
- `MailingAttempt – attempt_time, status (Успешно/Не успешно), server_response, mailing (FK → Mailing).` 
Попытка отправки.

Для всех моделей заданы `Meta` (`verbose_name`, `verbose_name_plural`) и метод `__str__`.

---

## 🔗 Основные маршруты

**Аутентификация (accounts):**
- /accounts/register/ — регистрация
- /accounts/login/ — вход
- /accounts/logout/ — выход
- /accounts/profile/ — профиль
- /accounts/profile/edit/ — редактирование профиля
- /accounts/verify-email/<pk>/<token>/ — подтверждение email

**Рассылки (mailing):**
- / — главная (счётчики)
- /clients/ — список клиентов
- /messages/ — список сообщений
- /mailings/ — список рассылок
- /mailings/<pk>/ — детальная рассылки
- /mailings/<pk>/send/ — запуск рассылки
- /statistics/ — статистика

**Админка:**
- /admin/ — админка Django

---

## 📨 Отправка рассылок

Логика отправки реализована в `mailing/services.py` → `send_mailing(mailing_id)`:

1. **Проверка времени** — если `now` не между `start_time` и `end_time`, возвращается ошибка.
2. **Получатели** — берутся все клиенты, связанные с рассылкой.
3. **Отправка** — для каждого клиента вызывается `send_mail()`. В dev-режиме письма печатаются в консоль 
(`EMAIL_BACKEND = console`).
4. **Попытки** — создаются через `MailingAttempt.objects.bulk_create()` (один запрос к БД).
5. **Результат** — возвращает `{'success': bool, 'message': str, 'sent': int, 'failed': int}`.

---

## 👥 Роли и права

- **Пользователь** — создаёт, просматривает, редактирует и удаляет только **своих** клиентов, сообщения и рассылки.
- **Менеджер** (группа «Менеджер») — видит **все** данные, но **не может** редактировать или удалять чужие объекты. 
Может просматривать пользователей сервиса.
- **Суперюзер** — полный доступ ко всему.

Группа «Менеджер» создаётся командой:
```bash
python manage.py create_manager_group
```

---

## ⚡ Кэширование (Redis)

- **Серверное** — счётчики на главной и статистика кэшируются в Redis.
  - Главная: ключ `home_stats_user_<id>`, TTL = 300 секунд.
  - Статистика: ключ `stats_user_<id>`, TTL = 300 секунд.
  - Настройка в `config/settings.py` → `CACHES` (база `/1`, порт `6380`).
- **Клиентское** — заголовок `Cache-Control: public, max-age=60` для главной и статистики, `max-age=31536000` 
для статики.

Проверка:
```bash
docker exec -it agromail-redis redis-cli -n 1 KEYS "*"
```

---

## 📌 Планы по доработке

- **Визуальный редактор писем** — WYSIWYG для тела письма.
- **Планировщик задач** (Celery + Redis) — автоматическая отправка в `start_time`.
- **REST API** — на Django REST Framework для интеграции с мобильным приложением.
- **Docker** — контейнеризация всего проекта (PostgreSQL + Redis + Django).
- **CI/CD** — GitHub Actions для автозапуска тестов.
- **Улучшение UI/UX** — добавить графики в статистику, фильтры в списки.

---

## 🧪 Тесты

В проекте **13 unit-тестов** (`django.test.TestCase`):

- **Модели** — валидация `start_time`/`end_time`, метод `update_status()` (3 теста).
- **Сервис отправки** — успешная отправка + `bulk_create` попыток, запрет отправки вне интервала (2 теста).
- **Права доступа** — пользователь видит только своих клиентов, менеджер — всех, запрет на редактирование чужого 
(3 теста).
- **Аутентификация** — регистрация с подтверждением email, запрет входа для неподтверждённых (2 теста).
- **Менеджер User** — автогенерация username, создание суперюзера (2 теста, `accounts/tests.py`).
- **Подтверждение email** — переход по токену активирует пользователя (1 тест, `accounts/tests.py`).

**Для запуска:**

```bash
python manage.py test
```
**Все тесты должны пройти со статусом OK.**

---

## 👨‍🌾 Об авторе

Александр **(BUMbiro)** — студент курса **Python-разработки**.  
Проект создан в рамках курсовой работы по **Django** и развивается как портфолио.

**Стек:** Django · PostgreSQL · Redis · Bootstrap 5 · Docker

**Репозиторий:** https://github.com/BUMbiro/AgroMail

---

## 📝 Лицензия

Это учебный проект. Не предназначен для коммерческого использования.